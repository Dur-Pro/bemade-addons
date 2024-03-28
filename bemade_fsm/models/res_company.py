from odoo import models, fields


class Company(models.Model):
    _inherit = "res.company"

    split_time_from_materials_on_service_work_orders = fields.Boolean(default=False)
    create_default_fsm_visit = fields.Boolean(default=False)
