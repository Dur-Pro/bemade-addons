from odoo import models, fields

class CaldavCalendar(models.Model):
    _name = 'caldav.calendar'
    _description = 'CalDAV Calendar'

    user_id = fields.Many2one('res.users', string='User', required=True, ondelete='cascade')
    name = fields.Char('Name', required=True)
    url = fields.Char('URL', required=True)
