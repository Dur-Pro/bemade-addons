from odoo import models, fields, api
import caldav
import logging

_logger = logging.getLogger(__name__)

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    caldav_uid = fields.Char('CalDAV UID')

    @api.model
    def create(self, values):
        event = super(CalendarEvent, self).create(values)
        if event._is_caldav_enabled():
            try:
                event.sync_to_caldav()
            except Exception as e:
                _logger.error(f"Failed to sync event to CalDAV: {e}")
        return event

    def write(self, values):
        result = super(CalendarEvent, self).write(values)
        if self._is_caldav_enabled():
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
                calendar = client.principal().calendars()[0]  # Assuming the first calendar
                vevent = calendar.add_event(event._get_icalendar())
                event.caldav_uid = vevent.vobject_instance.vevent.uid.value

    def remove_from_caldav(self):
        for event in self:
            if event.caldav_uid and event._is_caldav_enabled():
                client = event._get_caldav_client()
                calendar = client.principal().calendars()[0]  # Assuming the first calendar
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
                    calendar = client.principal().calendars()[0]  # Assuming the first calendar
                    events = calendar.events()

                    # Collect all current CalDAV UIDs for this user
                    current_uids = set(event.caldav_uid for event in self.search([('caldav_uid', '!=', False), ('create_uid', '=', user.id)]))

                    for event in events:
                        ical = event.icalendar()
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
        return bool(user.caldav_server_url and user.caldav_username and user.caldav_password)

    def _get_icalendar(self):
        vevent = f"""
BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:{self.caldav_uid}
DTSTAMP:{self.start.strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{self.start.strftime('%Y%m%dT%H%M%SZ')}
DTEND:{self.stop.strftime('%Y%m%dT%H%M%SZ')}
SUMMARY:{self.name}
DESCRIPTION:{self.description or ''}
LOCATION:{self.location or ''}
END:VEVENT
END:VCALENDAR
"""
        return vevent
