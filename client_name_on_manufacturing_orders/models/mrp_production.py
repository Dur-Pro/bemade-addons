from odoo import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    customer_ids = fields.Many2many(
        comodel_name='res.partner',
        compute="_compute_customers",
        string="Customers",
    )

    @api.depends('procurement_group_id')
    def _compute_customers(self):
        for rec in self:
            rec.customer_ids = (rec.mapped('procurement_group_id').
                                mapped('mrp_production_ids').
                                mapped('move_dest_ids').
                                mapped('group_id').
                                mapped('sale_id').
                                mapped('partner_id').ids)
