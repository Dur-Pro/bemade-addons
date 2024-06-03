from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company or self.env.user.company_id,
    )
    separate_time_on_work_orders = fields.Boolean(
        "Separate Time from Materials on Work Order",
        related="company_id.split_time_from_materials_on_service_work_orders",
        check_company=True,
        readonly=False,
    )
    create_default_fsm_visit = fields.Boolean(
        "Create Default Visit for FSM Sales Orders",
        related="company_id.create_default_fsm_visit",
        check_company=True,
        readonly=False,
    )
