from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    web_app_icon = fields.Binary(
        string="Web App Icon",
        related='company_id.web_app_icon',
        readonly=False
    )
    pwa_icon_192 = fields.Binary(
        string="PWA Icon 192x192",
        related='company_id.pwa_icon_192',
        readonly=True
    )
    pwa_icon_512 = fields.Binary(
        string="PWA Icon 512x512",
        related='company_id.pwa_icon_512',
        readonly=True
    )

    web_app_fgcolor = fields.Char(
        string="Foreground Color",
        related='company_id.web_app_fgcolor',
        readonly=False
    )
    web_app_bgcolor = fields.Char(
        string="Background Color",
        related='company_id.web_app_bgcolor',
        readonly=False
    )