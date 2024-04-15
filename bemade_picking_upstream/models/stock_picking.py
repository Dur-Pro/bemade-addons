from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    upstream_picking_ids = fields.One2many(
        compute="_compute_upstream_picking_ids",
        comodel_name="stock.picking",
        string="Upstream Transfers",
        help="Transfers that this transfer depends on for stock availability.",
        compute_sudo=True,
    )

    upstream_picking_count = fields.Integer(
        compute="_compute_upstream_picking_ids",
        compute_sudo=True,
    )

    @api.depends('move_lines', 'move_lines.move_orig_ids', 'move_lines.move_orig_ids.picking_id')
    def _compute_upstream_picking_ids(self):
        for rec in self:
            rec.upstream_picking_ids = rec.move_lines.mapped('move_orig_ids').mapped('picking_id') - rec
            rec.upstream_picking_count = len(rec.upstream_picking_ids)

    def action_view_upstream_transfers(self):
        return {
            'name': 'Upstream Transfers',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'domain': [('id', 'in', self.upstream_picking_ids.ids)],
            'view_mode': 'tree,kanban,form,calendar,map',
        }
