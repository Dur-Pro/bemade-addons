from odoo.tests import TransactionCase, Form, tagged

@tagged("-at_install", "post_install")
class TestSettings(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_partner_co = cls.env['res.partner'].create({
            'name': 'Test Co',
        })
        cls.test_co = cls.env['res.company'].create({
            'name': 'Test Co',
            'country_id': cls.env.ref('base.ca').id,

        })
        cls.env.user.company_id = cls.test_co

    def test_enabling_separate_time_on_work_orders(self):
        wizard = self.env['res.config.settings'].create({})
        self.assertFalse(
            self.test_co.split_time_from_materials_on_service_work_orders
        )
        with Form(wizard) as form:
            form.separate_time_on_work_orders = True
        self.assertTrue(
            self.test_co.split_time_from_materials_on_service_work_orders
        )

    def test_disabling_separate_time_on_work_orders(self):
        wizard = self.env['res.config.settings'].create({})
        self.test_co.split_time_from_materials_on_service_work_orders = True
        with Form(wizard) as form:
            form.separate_time_on_work_orders = False
        self.assertFalse(
            self.test_co.split_time_from_materials_on_service_work_orders
        )

    def test_enabling_create_default_fsm_visit(self):
        wizard = self.env['res.config.settings'].create({})
        self.test_co.create_default_fsm_visit = False
        with Form(wizard) as form:
            form.create_default_fsm_visit = True
        self.assertTrue(
            self.test_co.create_default_fsm_visit
        )

    def test_disabling_create_default_fsm_visit(self):
        wizard = self.env['res.config.settings'].create({})
        self.test_co.create_default_fsm_visit = True
        with Form(wizard) as form:
            form.create_default_fsm_visit = False
        self.assertFalse(
            self.test_co.create_default_fsm_visit
        )
