from odoo import models, fields
import caldav

class ResUsers(models.Model):
    _inherit = 'res.users'

    caldav_server_url = fields.Char('CalDAV Server URL')
    caldav_username = fields.Char('CalDAV Username')
    caldav_password = fields.Char('CalDAV Password')

    def _get_caldav_client(self):
        return caldav.DAVClient(url=self.caldav_server_url, username=self.caldav_username, password=self.caldav_password)

    def _is_caldav_enabled(self):
        return bool(self.caldav_server_url and self.caldav_username and self.caldav_password)
