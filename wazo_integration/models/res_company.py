from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    wazo_active = fields.Char(
        string='Wazo Tenant'
    )

    wazo_tenant = fields.Char(
        string='Wazo Tenant'
    )
    wazo_server_url = fields.Char(
        string='Wazo Server URL'
    )
    wazo_username = fields.Char(
        string='Wazo Username'
    )
    wazo_password = fields.Char(
        string='Wazo Password'
    )
