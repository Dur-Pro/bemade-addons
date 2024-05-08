from odoo import api, SUPERUSER_ID
from openupgradelib.openupgrade import rename_fields


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    field_spec = [
        ('sale.order', 'sale_order', 'margin_actual', 'gross_profit'),
        ('sale.order', 'sale_order', 'margin_percent_actual', 'gross_profit_percent'),
        ('sale.order.line', 'sale_order_line', 'margin_percent_vendor', 'gross_profit_percent_vendor'),
        ('sale.order.line', 'sale_order_line', 'margin_vendor', 'gross_profit_vendor'),
        ('sale.order.line', 'sale_order_line', 'margin_actual', 'gross_profit'),
        ('sale.order.line', 'sale_order_line', 'margin_percent_actual', 'gross_profit_percent'),
    ]
    rename_fields(env, field_spec)
    view_datas = env['ir.model.data'].search([
        ('module', '=', 'bemade_margin_vendor_pricelist'),
        ('model', '=', 'ir.ui.view')
    ])
    views = env['ir.ui.view'].browse(view_datas.mapped('res_id'))
    views.unlink()
