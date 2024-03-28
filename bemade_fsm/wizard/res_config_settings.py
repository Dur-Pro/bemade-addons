from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_bemade_fsm_separate_time_on_work_orders = fields.Boolean("Separate Time from Materials on Work Order")
    module_bemade_fsm_create_default_fsm_visit = fields.Boolean("Create Default Visit for FSM Sales Orders")

    def set_values(self):
        super().set_values()
        self.env.company.split_time_from_materials_on_service_work_orders = \
            self.module_bemade_fsm_separate_time_on_work_orders
        self.env.company.create_default_fsm_visit = self.module_bemade_fsm_create_default_fsm_visit

    def get_values(self):
        res = super().get_values()
        res.update({
            'module_bemade_fsm_separate_time_on_work_orders':
                self.env.company.split_time_from_materials_on_service_work_orders,
            'module_bemade_fsm_create_default_fsm_visit': self.env.company.create_default_fsm_visit
        })
        return res
