
from odoo import models, fields, api
import caldav
import logging
from icalendar import Calendar, Event, vCalAddress, vText

_logger = logging.getLogger(__name__)

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    caldav_uid = fields.Char('CalDAV UID')

    @api.model
    def create(self, values):
        event = super(CalendarEvent, self).create(values)
        if event._is_caldav_enabled() and not self.env.context.get('skip_caldav_sync'):
            try:
                event.sync_to_caldav()
            except Exception as e:
                _logger.error(f"Failed to sync event to CalDAV: {e}")
        return event

    def write(self, values):
        result = super(CalendarEvent, self).write(values)
        if self._is_caldav_enabled() and not self.env.context.get('skip_caldav_sync'):
            try:
                self.sync_to_caldav()
            except Exception as e:
                _logger.error(f"Failed to sync event to CalDAV: {e}")
        return result

    def unlink(self):
        if self._is_caldav_enabled():
            try:
                self.remove_from_caldav()
            except Exception as e:
                _logger.error(f"Failed to remove event from CalDAV: {e}")
        return super(CalendarEvent, self).unlink()

    def sync_to_caldav(self):
        for event in self:
            if event._is_caldav_enabled():
                client = event._get_caldav_client()
                calendar = client.calendar(url=event._get_caldav_calendar_url())
                caldav_event = calendar.add_event(event._get_icalendar())
                if caldav_event.id:
                    event.with_context(skip_caldav_sync=True).write({'caldav_uid': caldav_event.id})
                else:
                    _logger.error(f"Failed to sync event to CalDAV: Event ID not returned")

    def remove_from_caldav(self):
        for event in self:
            if event.caldav_uid and event._is_caldav_enabled():
                client = event._get_caldav_client()
                calendar = client.calendar(url=event._get_caldav_calendar_url())
                caldav_event = calendar.event_by_uid(event.caldav_uid)
                if caldav_event:
                    caldav_event.delete()

    @api.model
    def poll_caldav_server(self):
        """Poll the CalDAV server and synchronize events for all users"""
        _logger.info('Polling CalDAV server for updates...')
        users = self.env['res.users'].search([])
        for user in users:
            if user._is_caldav_enabled():
                try:
                    _logger.info(f'Polling CalDAV server for user {user.name}...')
                    client = user._get_caldav_client()
                    calendar = client.calendar(url=user.caldav_calendar_id.url)
                    events = calendar.events()

                    # Collect all current CalDAV UIDs for this user
                    current_uids = set(event.caldav_uid for event in self.search([('caldav_uid', '!=', False), ('create_uid', '=', user.id)]))

                    for event in events:
                        ical = event.icalendar_instance
                        uid = ical.subcomponents[0]['UID']
                        current_uids.discard(uid)  # Remove from the set of current UIDs
                        self.sync_event_from_ical(ical, user)

                    # Any UIDs remaining in current_uids are events that have been deleted on the CalDAV server
                    for uid in current_uids:
                        odoo_event = self.search([('caldav_uid', '=', uid), ('create_uid', '=', user.id)], limit=1)
                        if odoo_event:
                            odoo_event.unlink()
                except Exception as e:
                    _logger.error(f"Failed to poll CalDAV server for user {user.name}: {e}")

    def sync_event_from_ical(self, ical, user):
        event = ical.subcomponents[0]
        uid = event['UID']
        start = event['DTSTART'].dt
        end = event['DTEND'].dt
        summary = event['SUMMARY']
        description = event.get('DESCRIPTION', '')
        location = event.get('LOCATION', '')

        odoo_event = self.search([('caldav_uid', '=', uid), ('create_uid', '=', user.id)], limit=1)
        values = {
            'name': summary,
            'start': start,
            'stop': end,
            'description': description,
            'location': location,
            'create_uid': user.id,
        }

        if odoo_event:
            odoo_event.write(values)
        else:
            values['caldav_uid'] = uid
            self.create(values)

    def _get_caldav_client(self):
        user = self.env.user
        return caldav.DAVClient(url=user.caldav_server_url, username=user.caldav_username, password=user.caldav_password)

    def _is_caldav_enabled(self):
        user = self.env.user
        return bool(user.caldav_server_url and user.caldav_username and user.caldav_password and user.caldav_calendar_id)

    def _get_caldav_calendar_url(self):
        user = self.env.user
        return user.caldav_calendar_id.url

    def _get_icalendar(self):
        cal = Calendar()
        cal.add('prodid', '-//Odoo//')
        cal.add('version', '2.0')

        event = Event()
        event.add('summary', self.name)
        event.add('dtstart', self.start)
        event.add('dtend', self.stop)
        event.add('dtstamp', self.create_date)
        event.add('uid', self.caldav_uid)
        event.add('description', self.description or '')
        event.add('location', self.location or '')

        # Add attendees
        for attendee in self.attendee_ids:
            vattendee = vCalAddress('MAILTO:%s' % attendee.email)
            vattendee.params['cn'] = vText(attendee.partner_id.name)
            vattendee.params['ROLE'] = vText('REQ-PARTICIPANT')
            event.add('attendee', vattendee, encode=0)

        # Add organizer
        organizer = self.create_uid.partner_id
        if organizer:
            vorganizer = vCalAddress('MAILTO:%s' % organizer.email)
            vorganizer.params['cn'] = vText(organizer.name)
            vorganizer.params['ROLE'] = vText('CHAIR')
            event['organizer'] = vorganizer

        cal.add_component(event)

        return cal.to_ical().decode('utf-8')
