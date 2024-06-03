from .test_bemade_fsm_common import BemadeFSMBaseTest
from odoo.tests import Form


class TestTaskReport(BemadeFSMBaseTest):
    def test_split_time_materials_setting(self):
        with Form(self.env['res.config.settings']) as settings:
            settings.separate_time_on_work_orders = True

        with Form(self.env['res.config.settings']) as new_settings:
            self.assertTrue(settings.separate_time_on_work_orders)

        so = self._generate_sale_order()
        service_product = self._generate_product()
        material_product = self._generate_product(
            name="Material Product",
            product_type='product',
            service_tracking='no',
        )
        visit = self._generate_visit(sale_order=so)
        sol = self._generate_sale_order_line(sale_order=so, product=service_product)
        sol2 = self._generate_sale_order_line(sale_order=so, product=material_product)
        so.action_confirm()
        task = visit.task_id

        html_content = self.env['ir.actions.report']._render(
            'industry_fsm_report.worksheet_custom',
            [task.id],
        )[0].decode('utf-8').split('\n')

        strings_to_find = [
            "<h2>Materials</h2>",
            "<span>Material Product</span>"
        ]

        for line in strings_to_find:
            line_found = False
            for html_line in html_content:
                if line in html_line:
                    line_found = True
            self.assertTrue(line_found, f"{line} should be in file.")
