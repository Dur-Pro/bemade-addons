from odoo import models


class TaskCustomReport(models.AbstractModel):
    _inherit = "report.industry_fsm_report.worksheet_custom"

    def _get_report_values(self, docids, data=None):
        vals = super()._get_report_values(docids, data)
        split_time_materials = (
            self.env.company.split_time_from_materials_on_service_work_orders
        )
        vals.update({"split_time_materials": split_time_materials})
        return vals
