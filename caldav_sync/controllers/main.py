from odoo import http
from odoo.http import request
import logging
import caldav
from caldav.elements import dav, cdav
from datetime import datetime

_logger = logging.getLogger(__name__)

class CaldavController(http.Controller):

    @http.route('/caldav_sync/sync', type='json', auth='user')
    def sync(self, **kwargs):
        # Fetch user credentials and server settings from Odoo
        user = request.env.user
        server_url = user.caldav_server_url
        username = user.caldav_username
        password = user.caldav_password

        # Connect to the CalDAV server
        client = caldav.DAVClient(url=server_url, username=username, password=password)
        principal = client.principal()
        calendars = principal.calendars()

        for calendar in calendars:
            events = calendar.events()
            for event in events:
                ical = event.icalendar()
                self.sync_event(ical)

        return {'status': 'success', 'message': 'Synchronization completed'}

    def sync_event(self, ical):
        event = ical.subcomponents[0]
        uid = event['UID']
        start = event['DTSTART'].dt
        end = event['DTEND'].dt
        summary = event['SUMMARY']
        description = event.get('DESCRIPTION', '')
        location = event.get('LOCATION', '')

        # Search for an existing event in Odoo
        odoo_event = request.env['calendar.event'].search([('caldav_uid', '=', uid)], limit=1)
        values = {
            'name': summary,
            'start': start,
            'stop': end,
            'description': description,
            'location': location,
        }

        if odoo_event:
            odoo_event.write(values)
        else:
            values['caldav_uid'] = uid
            request.env['calendar.event'].create(values)
