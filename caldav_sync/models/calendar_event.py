from odoo import models, api, fields
import caldav
from caldav.elements import dav, cdav
import logging

_logger = logging.getLogger(__name__)

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    caldav_uid = fields.Char(string='CalDAV UID', readonly=True)

    @api.model
    def create(self, vals):
        event = super(CalendarEvent, self).create(vals)
        event.sync_to_caldav()
        return event

    def write(self, vals):
        res = super(CalendarEvent, self).write(vals)
        self.sync_to_caldav()
        return res

    def unlink(self):
        for event in self:
            event.remove_from_caldav()
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

    def sync_to_caldav(self):
        if not self._is_caldav_enabled():
            return
        client = self._get_caldav_client()
        calendar = client.calendar(self.env.user.caldav_calendar_url)
        for event in self:
            ical_event = event._get_icalendar()
            if event.caldav_uid:
                caldav_event = calendar.event_by_uid(event.caldav_uid)
                caldav_event.save(ical_event)
            else:
                caldav_event = calendar.add_event(ical_event)
                event.caldav_uid = caldav_event.id

    def remove_from_caldav(self):
        if not self._is_caldav_enabled():
            return
        client = self._get_caldav_client()
        calendar = client.calendar(self.env.user.caldav_calendar_url)
        for event in self:
            if event.caldav_uid:
                caldav_event = calendar.event_by_uid(event.caldav_uid)
                caldav_event.delete()

    def _get_icalendar(self):
        from icalendar import Calendar, Event
        calendar = Calendar()
        calendar.add('prodid', '-//Odoo//mxm.dk//')
        calendar.add('version', '2.0')

        for event in self:
            ical_event = Event()
            ical_event.add('uid', event.caldav_uid or '')
            ical_event.add('dtstamp', event.write_date)
            ical_event.add('dtstart', event.start)
            ical_event.add('dtend', event.stop)
            ical_event.add('summary', event.name)
            ical_event.add('description', event.description)
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
        calendar = client.calendar(self.env.user.caldav_calendar_url)
        events = calendar.events()
        for caldav_event in events:
                ical_event = caldav_event.icalendar_instance
                self.sync_event_from_ical(ical_event)

    def sync_event_from_ical(self, ical_event):
        from icalendar import Event
        for component in ical_event.subcomponents:
            if isinstance(component, Event):
                uid = str(component.get('uid'))
                event = self.search([('caldav_uid', '=', uid)], limit=1)
                if not event:
                    self.create({
                        'name': str(component.get('summary')),
                        'start': component.decoded('dtstart'),
                        'stop': component.decoded('dtend'),
                        'description': str(component.get('description')),
                        'location': str(component.get('location')),
                        'caldav_uid': uid,
                    })
                else:
                    event.write({
                        'name': str(component.get('summary')),
                        'start': component.decoded('dtstart'),
                        'stop': component.decoded('dtend'),
                        'description': str(component.get('description')),
                        'location': str(component.get('location')),
                    })
