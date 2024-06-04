from odoo.addons.sale_mrp.tests.test_sale_mrp_flow import TestSaleMrpFlowCommon
from odoo.tests import Form, tagged


@tagged('-at_install', 'post_install')
class TestMrpProduction(TestSaleMrpFlowCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref)

    def _setup_products(self):
        route_manufacture = self.company_data['default_warehouse'].manufacture_pull_id.route_id
        route_mto = self.company_data['default_warehouse'].mto_pull_id.route_id
        product_a = self._create_product('Product A', self.uom_unit, routes=[route_manufacture, route_mto])
        product_c = self._create_product('Product C', self.uom_kg)
        product_b = self._create_product('Product B', self.uom_dozen, routes=[route_manufacture, route_mto])
        product_d = self._create_product('Product D', self.uom_unit, routes=[route_manufacture, route_mto])
        # Bill of materials for Product A.
        with Form(self.env['mrp.bom']) as f:
            f.product_tmpl_id = product_a.product_tmpl_id
            f.product_qty = 2
            f.product_uom_id = self.uom_dozen
            with f.bom_line_ids.new() as line:
                line.product_id = product_b
                line.product_qty = 3
                line.product_uom_id = self.uom_unit
            with f.bom_line_ids.new() as line:
                line.product_id = product_c
                line.product_qty = 300.0
                line.product_uom_id = self.uom_gm
            with f.bom_line_ids.new() as line:
                line.product_id = product_d
                line.product_qty = 4
                line.product_uom_id = self.uom_unit
        return product_a

    def _create_order(self, partner_name: str, product):
        order_form = Form(self.env['sale.order'])
        order_form.partner_id = self.env['res.partner'].create({'name': partner_name})
        with order_form.order_line.new() as line:
            line.product_id = product
            line.product_uom = self.uom_dozen
            line.product_uom_qty = 10
        return order_form.save()

    def test_mo_single_client_correctly_listed(self):
        product_a = self._setup_products()

        order = self._create_order('Test Partner', product_a)
        order.action_confirm()
        # A sales order creating an MO should have its partner listed in the MO's customer_ids field

        self.assertNotEquals(order.mrp_production_count, 0)
        for mo in order.mrp_production_ids:
            self.assertIn(order.partner_id, mo.customer_ids)

    def test_mo_multiple_so_clients_correctly_listed(self):
        product_a = self._setup_products()
        order1 = self._create_order('Test Partner 1', product_a)
        order2 = self._create_order('Test Partner 2', product_a)
        order1.action_confirm()
        order2.action_confirm()

        # Merge the MOs together so that the resulting MO is linked to multiple SOs
        (order1.mrp_production_ids | order2.mrp_production_ids).action_merge()

        self.assertTrue(order1.mrp_production_ids)
        self.assertTrue(order2.mrp_production_ids)
        self.assertEqual(order1.mrp_production_ids, order2.mrp_production_ids)
        for mo in order1.mrp_production_ids:
            self.assertIn(order1.partner_id, mo.customer_ids)
            self.assertIn(order2.partner_id, mo.customer_ids)
