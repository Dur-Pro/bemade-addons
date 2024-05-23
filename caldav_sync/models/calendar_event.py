import uuid
from odoo import models, api, fields
import caldav
import logging
from datetime import datetime
from icalendar import Calendar, Event

_logger = logging.getLogger(__name__)

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    caldav_uid = fields.Char(string='CalDAV UID', readonly=True)

    @api.model
    def create(self, vals):
        if not vals.get('caldav_uid'):
            vals['caldav_uid'] = str(uuid.uuid4())
        event = super(CalendarEvent, self).create(vals)
        if not self.env.context.get('caldav_no_sync'):
            try:
                _logger.debug(f"Creating event {event.name} in CalDAV")
                event.sync_create_to_caldav()
            except Exception as e:
                _logger.error(f"Failed to create event in CalDAV server: {e}")
        return event

    def write(self, vals):
        res = super(CalendarEvent, self).write(vals)
        if not self.env.context.get('caldav_no_sync'):
            try:
                _logger.debug(f"Updating event {self.name} in CalDAV")
                self.sync_update_to_caldav()
            except Exception as e:
                _logger.error(f"Failed to update event in CalDAV server: {e}")
        return res

    def unlink(self):
        if not self.env.context.get('caldav_no_sync'):
            for event in self:
                try:
                    _logger.debug(f"Removing event {event.name} from CalDAV")
                    event.sync_remove_from_caldav()
                except Exception as e:
                    _logger.error(f"Failed to delete event from CalDAV server: {e}")
        return super(CalendarEvent, self).unlink()

    def _is_caldav_enabled(self):
        user = self.env.user
        return all([user.caldav_calendar_url, user.caldav_username, user.caldav_password])

    def _get_caldav_client(self):
        user = self.env.user
        return caldav.DAVClient(
            url=user.caldav_calendar_url,
            username=user.caldav_username,
            password=user.caldav_password
        )

    def sync_create_to_caldav(self):
        if not self._is_caldav_enabled():
            return
        client = self._get_caldav_client()
        calendar = client.calendar(url=self.env.user.caldav_calendar_url)
        for event in self:
            ical_event = event._get_icalendar()
            try:
                _logger.debug(f"Creating new CalDAV event for {event.name}")
                caldav_event = calendar.add_event(ical_event)
                caldav_uid = caldav_event.vobject_instance.vevent.uid.value
                _logger.debug(f"New CalDAV UID: {caldav_uid}")
                event.with_context(caldav_no_sync=True).write({'caldav_uid': caldav_uid})
            except Exception as e:
                _logger.error(f"Failed to sync event to CalDAV server: {e}")

    def sync_update_to_caldav(self):
        if not self._is_caldav_enabled():
            return
        client = self._get_caldav_client()
        calendar = client.calendar(url=self.env.user.caldav_calendar_url)
        for event in self:
            ical_event = event._get_icalendar()
            try:
                _logger.debug(f"Updating existing CalDAV event {event.caldav_uid}")
                calendar.save_event(ical=ical_event)
            except Exception as e:
                _logger.error(f"Failed to sync event to CalDAV server: {e}")

    def sync_remove_from_caldav(self):
        if not self._is_caldav_enabled():
            return
        client = self._get_caldav_client()
        calendar = client.calendar(url=self.env.user.caldav_calendar_url)
        for event in self:
            if event.caldav_uid:
                try:
                    _logger.debug(f"Removing CalDAV event {event.caldav_uid}")
                    caldav_event = calendar.object_by_uid(event.caldav_uid)
                    caldav_event.delete()
                except caldav.error.NotFoundError:
                    _logger.warning(f"CalDAV event {event.caldav_uid} not found on server.")
                except Exception as e:
                    _logger.error(f"Failed to remove event from CalDAV server: {e}")

    def _get_icalendar(self):
        calendar = Calendar()
        calendar.add('prodid', '-//Odoo//mxm.dk//')
        calendar.add('version', '2.0')

        for event in self:
            ical_event = Event()
            ical_event.add('uid', event.caldav_uid)
            ical_event.add('dtstamp', event.write_date.replace(tzinfo=None))
            ical_event.add('dtstart', event.start.replace(tzinfo=None))
            ical_event.add('dtend', event.stop.replace(tzinfo=None))
            if event.name:
                ical_event.add('summary', event.name)
            if event.description:
                ical_event.add('description', event.description)
            if event.location:
                ical_event.add('location', event.location)
            calendar.add_component(ical_event)

        return calendar.to_ical()

    @api.model
    def poll_caldav_server(self):
        users = self.env['res.users'].search([('caldav_calendar_url', '!=', False)])
        for user in users:
            try:
                self.with_user(user).poll_user_caldav_server()
            except Exception as e:
                _logger.error(f"Failed to poll CalDAV server for user {user.name}: {e}")

    def poll_user_caldav_server(self):
        if not self._is_caldav_enabled():
            return
        client = self._get_caldav_client()
        calendar = client.calendar(url=self.env.user.caldav_calendar_url)
        events = calendar.events()
        caldav_uids = set()

        _logger.info(f"Polling CalDAV server for user {self.env.user.name}")

        for caldav_event in events:
            ical_event = caldav_event.icalendar_instance
            self.sync_event_from_ical(ical_event)
            for component in ical_event.subcomponents:
                if isinstance(component, Event):
                    uid = str(component.get('uid'))
                    caldav_uids.add(uid)

        _logger.info(f"CalDAV UIDs fetched: {caldav_uids}")

        # Remove Odoo events that no longer exist on the CalDAV server
        odoo_events = self.search([('caldav_uid', '!=', False)])
        for event in odoo_events:
            if event.caldav_uid not in caldav_uids:
                _logger.info(f"Deleting orphan event {event.name} with UID {event.caldav_uid}")
                event.with_context(caldav_no_sync=True).unlink()

    def sync_event_from_ical(self, ical_event):
        for component in ical_event.subcomponents:
            if isinstance(component, Event):
                uid = str(component.get('uid'))
                event = self.search([('caldav_uid', '=', uid)], limit=1)
                start = component.decoded('dtstart')
                stop = component.decoded('dtend')
                if isinstance(start, datetime):
                    start = start.replace(tzinfo=None)
                if isinstance(stop, datetime):
                    stop = stop.replace(tzinfo=None)
                if not event:
                    _logger.info(f"Creating new event {str(component.get('summary'))} with UID {uid}")
                    self.with_context({'caldav_no_sync': True}).create({
                        'name': str(component.get('summary')),
                        'start': start,
                        'stop': stop,
                        'description': str(component.get('description')),
                        'location': str(component.get('location')),
                        'caldav_uid': uid,
                    })
                else:
                    _logger.info(f"Updating existing event {event.name} with UID {uid}")
                    event.with_context({'caldav_no_sync': True}).write({
                        'name': str(component.get('summary')),
                        'start': start,
                        'stop': stop,
                        'description': str(component.get('description')),
                        'location': str(component.get('location')),
                    })
