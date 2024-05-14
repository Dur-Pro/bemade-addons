from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import requests
import json


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    wazo_tenant = fields.Char(
        related='company_id.wazo_tenant',
        string='Wazo Tenant',
        readonly=False
    )
    wazo_server_url = fields.Char(
        related='company_id.wazo_server_url',
        string='Wazo Server URL',
        readonly=False
    )
    wazo_username = fields.Char(
        related='company_id.wazo_username',
        string='Wazo Username',
        readonly=False
    )
    wazo_password = fields.Char(
        related='company_id.wazo_password',
        string='Wazo Password',
        readonly=False
    )

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        company = self.env.user.company_id
        url = self.wazo_server_url
        username = self.wazo_username
        password = self.wazo_password
        tenant = self.wazo_tenant
        if url and username and password and tenant:
            try:
                self._check_wazo_connection(url, username, password, tenant)
            except ValidationError as e:
                raise ValidationError(_("Failed to connect to Wazo server: %s") % e)

    def _check_wazo_connection(self, url, username, password, tenant):
        payload = {
            "backend": "wazo_user",
            "expire": "3600",
            "login": username,
            "password": password,
        }
        headers = {
            'Content-Type': 'application/json',
            'Wazo-Tenant': tenant
        }
        response = requests.post(f"{url}/api/auth/0.1/token", headers=headers, json=payload, verify=False)
        if response.status_code != 200:
            raise ValidationError(response.json().get('message', 'Unknown error'))