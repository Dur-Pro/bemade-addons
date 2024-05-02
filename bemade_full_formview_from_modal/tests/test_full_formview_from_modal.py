from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestFullFormviewFromModal(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.parent = cls.env['res.partner'].create({'name': 'Test parent', })
        cls.child = cls.env['res.partner'].create({'name': 'Test Child', 'parent_id': cls.parent.id})

    def test_tour(self):
        self.start_tour("/web", 'full_formview_from_modal_tour', login="demo")
