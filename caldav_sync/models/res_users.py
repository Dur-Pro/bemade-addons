from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    caldav_calendar_url = fields.Char(string='CalDAV Calendar URL')
    caldav_username = fields.Char(string='CalDAV Username')
    caldav_password = fields.Char(string='CalDAV Password', password=True)

    def is_caldav_enabled(self):
        self.ensure_one()
        return bool(self.caldav_calendar_url and self.caldav_username and self.caldav_password)