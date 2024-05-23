from odoo import models, fields, api
import caldav
import logging

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    caldav_server_url = fields.Char('CalDAV Server URL')
    caldav_username = fields.Char('CalDAV Username')
    caldav_password = fields.Char('CalDAV Password')
    caldav_calendar_id = fields.Many2one('caldav.calendar', string='CalDAV Calendar')  # Updated field

    @api.model
    def _is_caldav_enabled(self):
        self.ensure_one()
        return bool(self.caldav_server_url and self.caldav_username and self.caldav_password and self.caldav_calendar_id)

    def fetch_caldav_calendars(self):
        self.ensure_one()
        client = caldav.DAVClient(url=self.caldav_server_url, username=self.caldav_username, password=self.caldav_password)
        principal = client.principal()
        calendars = principal.calendars()
        caldav_calendar_model = self.env['caldav.calendar']
        caldav_calendar_model.search([('user_id', '=', self.id)]).unlink()  # Clear existing calendars
        for calendar in calendars:
            caldav_calendar_model.create({
                'user_id': self.id,
                'name': calendar.name,
                'url': str(calendar.url),
            })
        return True

    def _get_caldav_client(self):
        self.ensure_one()
        return caldav.DAVClient(url=self.caldav_server_url, username=self.caldav_username, password=self.caldav_password)
