from odoo import models, fields, api
from PIL import Image
import base64
from io import BytesIO


class Company(models.Model):
    _inherit = 'res.company'

    web_app_icon = fields.Binary(string="Web App Icon")
    pwa_icon_192 = fields.Binary(string="PWA Icon 192x192")
    pwa_icon_512 = fields.Binary(string="PWA Icon 512x512")

    web_app_fgcolor = fields.Char(
        string="Foreground Color",
        default='#FFFFFF'
    )

    web_app_bgcolor = fields.Char(
        string="Background Color",
        default='#714B67'
    )

    @api.model
    def create(self, vals):
        record = super(Company, self).create(vals)
        record.generate_pwa_icons()
        return record

    def write(self, vals):
        result = super(Company, self).write(vals)
        if 'web_app_icon' in vals:
            self.generate_pwa_icons()
        return result

    def generate_pwa_icons(self):
        if self.web_app_icon:
            image_stream = BytesIO(base64.b64decode(self.web_app_icon))
            image = Image.open(image_stream)
            sizes = {192: 'pwa_icon_192', 512: 'pwa_icon_512'}
            for size, field_name in sizes.items():
                resized_image = image.resize((size, size), Image.ANTIALIAS)
                stream = BytesIO()
                resized_image.save(stream, format='PNG')
                resized_binary = base64.b64encode(stream.getvalue())
                setattr(self, field_name, resized_binary)