from odoo.tests import TransactionCase, tagged
from odoo.addons.bemade_utils import patch_test


@tagged("-at_install", "post_install")
class TestA(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_method_a(self):
        self.assertFalse(True)


@patch_test(TestA.test_method_a)
def test_redefining_test(self):
    self.assertTrue(True)
