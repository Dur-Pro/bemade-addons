from .test_bemade_fsm_common import BemadeFSMBaseTest
from odoo.tests.common import tagged, Form
from odoo import Command


@tagged('post_install', '-at_install')
class TaskTest(BemadeFSMBaseTest):

    @classmethod
    def setUpClass(cls):
        # Chose to set up all tests the same way since this code was becoming very redundant
        super().setUpClass()
        cls.user = cls._generate_project_manager_user('Bob', 'Bob')

    def _generate_so_with_multilevel_task_template(self):
        so = self._generate_sale_order()
        template = self._generate_task_template(names=['Parent', 'Child', 'Grandchild'], structure=[2, 1])
        product = self._generate_product(task_template=template)
        sol = self._generate_sale_order_line(sale_order=so, product=product)
        return so, sol

    def test_reassigning_assignment_propagating_task_changes_subtasks(self):
        so, sol = self._generate_so_with_multilevel_task_template()
        so.action_confirm()
        task = sol.task_id

        task.propagate_assignment = True
        task.write({
            'user_ids': [Command.set([self.user.id])],
            'propagate_assignment': True,
        })

        self.assertTrue(all([t.user_ids == self.user for t in task | task._get_all_subtasks()]))

    def test_reassigning_task_doesnt_propagate_by_default(self):
        so, sol = self._generate_so_with_multilevel_task_template()
        so.action_confirm()
        task = sol.task_id

        task.write({
            'user_ids': [Command.set([self.user.id])],
        })

        self.assertFalse(any([t.user_ids for t in task.child_ids.child_ids]))

    def test_unset_propagate_assignment_unsets_for_all_children(self):
        so, sol = self._generate_so_with_multilevel_task_template()
        so.action_confirm()
        task = sol.task_id
        # First, set propagation and assign
        task.propagate_assignment = True
        task.write({
            'user_ids': [Command.set([self.user.id])]
        })
        # Then, unset propagation for the children and re-set assignment
        task.child_ids.write({'propagate_assignment': False})
        self.assertFalse(any([t.propagate_assignment for t in task._get_all_subtasks()]))
        # Then, test that assigning the parent only assigns its children, not its grandchildren
        task.write({
            'user_ids': [Command.set([])]
        })
        self.assertTrue(all([not t.user_ids for t in task | task.child_ids]))
        self.assertTrue(all([t.user_ids == self.user for t in task.child_ids.child_ids]))

    def test_task_gets_work_order_contacts_from_sale_order(self):
        so, sol = self._generate_so_with_multilevel_task_template()
        work_order_contacts = self._generate_partner(parent=so.partner_id) | self._generate_partner(
            parent=so.partner_id)
        so.write({'work_order_contacts': [(6, 0, work_order_contacts.ids)]})

        so.action_confirm()
        task = sol.task_id

        self.assertEqual(task.work_order_contacts, so.work_order_contacts)
        # Just a safeguard to make sure we set it properly on the SO
        self.assertEqual(len(task.work_order_contacts), 2)
        # Make sure all subtasks got the same
        for subtask in task._get_all_subtasks():
            self.assertEqual(subtask.work_order_contacts, so.work_order_contacts)

    def test_task_gets_site_contacts_from_sale_order(self):
        so, sol = self._generate_so_with_multilevel_task_template()
        site_contacts = self._generate_partner(parent=so.partner_id) | self._generate_partner(parent=so.partner_id)
        so.write({'site_contacts': [(6, 0, site_contacts.ids)]})

        so.action_confirm()
        task = sol.task_id

        self.assertEqual(task.site_contacts, so.site_contacts)
        # Just a safeguard to make sure we set it properly on the SO
        self.assertEqual(len(task.site_contacts), 2)
        # Make sure all subtasks got the same
        for subtask in task._get_all_subtasks():
            self.assertEqual(subtask.site_contacts, so.site_contacts)

    def test_task_gets_work_order_contacts_from_parent(self):
        so, sol = self._generate_so_with_multilevel_task_template()
        work_order_contacts = self._generate_partner(parent=so.partner_id) | self._generate_partner(parent=so.partner_id)
        so.write({'work_order_contacts': [(6, 0, work_order_contacts.ids)]})

        so.action_confirm()
        task = sol.task_id
        task.write({'work_order_contacts': [Command.link(self._generate_partner(parent=so.partner_id).id)]})
        for subtask in task._get_all_subtasks():
            self.assertEqual(subtask.work_order_contacts, task.work_order_contacts)
        with Form(task) as task_form:
            with task_form.child_ids.new() as subtask:
                subtask.name = "Subtask 1"
        subtask = task.child_ids[-1]
        self.assertEqual(subtask.work_order_contacts, task.work_order_contacts)

    def test_task_gets_site_contacts_from_parent(self):
        so, sol = self._generate_so_with_multilevel_task_template()
        site_contacts = self._generate_partner(parent=so.partner_id) | self._generate_partner(parent=so.partner_id)
        so.write({'site_contacts': [(6, 0, site_contacts.ids)]})

        so.action_confirm()
        task = sol.task_id
        task.write({'site_contacts': [Command.link(self._generate_partner(parent=so.partner_id).id)]})
        for subtask in task._get_all_subtasks():
            self.assertEqual(subtask.site_contacts, task.site_contacts)
        with Form(task) as task_form:
            with task_form.child_ids.new() as subtask:
                subtask.name = "Subtask 1"
        subtask = task.child_ids[-1]
        self.assertEqual(subtask.site_contacts, task.site_contacts)
