from odoo import models, fields, api
from datetime import timedelta

class TransferPropertyWizard(models.TransientModel):
    _name = 'transfer.property.wizard'
    _description = 'Transfer Property Wizard'

    property_id = fields.Many2one(
        comodel_name='res.partner',
        string='Property',
        domain=[('is_property', '=', True)],
        required=True
    )

    new_owner_id = fields.Many2many(
        comodel_name='res.partner',
        string='New Owner',
        required=True,
        domain=[('is_property', '=', False)],
    )

    transfer_date = fields.Date(
        string='Transfer Date',
        required=True,
        default=fields.Date.today()
    )

    def action_transfer_property(self):
        if self.property_id.relation_property_ids.filtered("active"):
            for old_owner_relation in self.property_id.relation_property_ids.filtered("active"):
                if old_owner_relation.date_start and old_owner_relation.date_start >= self.transfer_date:
                    old_owner_relation.unlink()
                else:
                    old_owner_relation.write({'date_end': self.transfer_date - timedelta(days=1)})
                old_owner_relation.this_partner_id._compute_owner()
        for new_owner in self.new_owner_id:
            self.env['res.partner.relation.all'].create({
                'this_partner_id': new_owner.id,
                'other_partner_id': self.property_id.id,
                'type_id': self.env.ref('bemade_sethy_configuration.partner_relation_property').id,
                'date_start': self.transfer_date,
            })
            new_owner._compute_owner()
        return {'type': 'ir.actions.act_window_close'}