from odoo import models, fields, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_back_to_draft(self):
        self.ensure_one()
        if self.state != 'cancel':
            raise UserError(_(
                'Only manufacturing orders in canceled'
                'state can be set back to draft.'
            ))
        self.state = False
        return True
