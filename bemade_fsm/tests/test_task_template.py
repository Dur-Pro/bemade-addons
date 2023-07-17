from .test_bemade_fsm_common import BemadeFSMBaseTest
from odoo.tests.common import HttpCase, tagged, Form
from odoo.exceptions import MissingError
from odoo import Command
from psycopg2.errors import ForeignKeyViolation


@tagged("-at_install", "post_install")
class TestTaskTemplateCommon(BemadeFSMBaseTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PLANNED_HOURS = 6
        hours_uom = cls.env['uom.uom'].search([('name', '=', 'Hour')]) or False
        # Test product to use with the various tests
        cls.task1 = cls.env['project.task.template'].create({
            'name': 'Template 1',
        })

        cls.project = cls.env.ref('industry_fsm.fsm_project')

        cls.product_task_global_project = cls._generate_product(name='Test Product 1', task_template=cls.task1)
        cls.project_template = cls._generate_fsm_project('Test Project Template')
        cls.product_task_in_project = cls._generate_product(name='Test Product 2', project=cls.project_template,
                                                            service_tracking='task_in_project', task_template=cls.task1)

        # Set up a task template tree with 2 children and 1 grandchild
        cls.parent_task = cls._generate_task_template(structure=[2, 1],
                                                      names=['Parent Template', 'Child Template',
                                                             'Grandchild Template'])
        cls.child_task_1 = cls.parent_task.subtasks[0]
        cls.child_task_2 = cls.parent_task.subtasks[1]
        cls.grandchild_task = cls.child_task_1.subtasks[0]

        # Create products using the task tree we just created
        cls.product_task_tree_global_project = cls._generate_product(name='Test Product 3',
                                                                     task_template=cls.parent_task)
        cls.product_task_tree_in_project = cls._generate_product(name="Test Product 2", project=cls.project_template,
                                                                 service_tracking='task_in_project',
                                                                 task_template=cls.parent_task)


@tagged('-at_install', 'post_install')
class TestTaskTemplate(TestTaskTemplateCommon):

    def test_delete_task_template(self):
        """User should never be able to delete a task template used on a product"""
        with self.assertRaises(ForeignKeyViolation):
            self.task1.unlink()

    def test_delete_subtask_template(self):
        """ Deletion of a child task should be OK even if the parent is on a product. Children of the deleted
        subtask should be deleted."""
        self.child_task_1.unlink()
        # Reading deleted child's name field should be impossible
        with self.assertRaises(MissingError):
            test = self.grandchild_task.name

    def test_dissociating_customer_resets_equipment_appropriately(self):
        partner1 = self._generate_partner()
        partner2 = self._generate_partner()
        equipment1 = self._generate_equipment(partner=partner1)
        form = Form(self.task1)
        form.customer = partner1
        form.equipment_ids.add(equipment1)

        # Switching the partner should trigger on_change that makes sure equipments are linked to the new partner
        form.customer = partner2

        self.assertFalse(equipment1 in self.task1.equipment_ids)


@tagged('-at_install', 'post_install', 'slow')
class TestTaskTemplateTour(HttpCase, TestTaskTemplateCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._generate_project_manager_user('Mister PM', 'misterpm')

    def test_task_template_tour(self):
        self.start_tour('/web', 'task_template_tour',
                        login='misterpm', )
