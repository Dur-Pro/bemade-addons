from odoo import models, fields, api, _
from odoo.tools.float_utils import float_is_zero, float_compare


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    gross_profit = fields.Monetary("Gross Profit", compute='_compute_margin_actual', store=False)

    gross_profit_percent = fields.Float(
        string='Gross Profit (%)',
        compute='_compute_margin_actual',
        store=False,
        group_operator='avg'
    )

    @api.depends('order_line.gross_profit', 'amount_untaxed')
    def _compute_margin_actual(self):
        for order in self:
            order.gross_profit = sum(order.order_line.mapped('gross_profit'))
            order.gross_profit_percent = order.amount_untaxed and order.gross_profit / order.amount_untaxed


