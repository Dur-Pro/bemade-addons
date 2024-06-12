from odoo.tests import tagged
from .test_bemade_fsm_common import BemadeFSMBaseTest
from datetime import date, timedelta


@tagged("-at_install", "post_install")
class FSMVisitTest(BemadeFSMBaseTest):
    def test_create_visit_sets_name_on_section(self):
        so = self._generate_sale_order()
        self._generate_sale_order_line(sale_order=so)

        visit = self._generate_visit(so)

        self.assertTrue(visit.so_section_id)
        self.assertEqual(visit.so_section_id.name, visit.label)

    def test_change_visit_section_name(self):
        so = self._generate_sale_order()
        visit = self._generate_visit(so, label="First Label")
        line = visit.so_section_id

        line.name = "Second Label"

        self.assertEqual(visit.label, "Second Label")

    def test_change_visit_label_changes_section_name(self):
        so = self._generate_sale_order()
        visit = self._generate_visit(so, label="First Label")
        line = visit.so_section_id

        visit.label = "Second Label"

        self.assertEqual(line.name, "Second Label")

    def test_visit_completes_when_task_completes(self):
        so = self._generate_sale_order()
        visit = self._generate_visit(so)
        self._generate_sale_order_line(so)
        so.action_confirm()
        task = so.order_line.filtered(lambda line: line.task_id).task_id

        task.action_fsm_validate()

        self.assertTrue(visit.is_completed)

    def test_visit_shows_invoiced_when_invoiced(self):
        so = self._generate_sale_order()
        visit = self._generate_visit(so)
        self._generate_sale_order_line(so)
        so.action_confirm()
        task = so.order_line.filtered(lambda line: line.task_id).task_id
        task.action_fsm_validate()

        self._invoice_sale_order(so)

        self.assertTrue(visit.is_invoiced)

    def test_visit_groups_section_tasks_when_confirmed(self):
        so, visit, sol1, sol2 = self._generate_so_with_one_visit_two_lines()

        so.action_confirm()

        visit_task = visit.task_id
        self.assertTrue(visit_task)
        visit_subtasks = visit_task.child_ids
        self.assertTrue(
            visit_subtasks
            and sol1.task_id in visit_subtasks
            and sol2.task_id in visit_subtasks
        )

    def test_visit_task_gets_correct_due_date_on_confirmation(self):
        so, visit, sol1, sol2 = self._generate_so_with_one_visit_two_lines()

        so.action_confirm()

        visit_task = visit.task_id
        self.assertEqual(visit_task.date_deadline, visit.approx_date)

    def test_visit_task_gets_correct_duration_on_confirmation(self):
        partner = self._generate_partner()
        so = self._generate_sale_order(partner=partner)
        visit = self._generate_visit(sale_order=so)
        sol1 = self._generate_sale_order_line(sale_order=so, qty=4.0)
        sol2 = self._generate_sale_order_line(sale_order=so, qty=4.0)
        visit.approx_date = date.today() + timedelta(days=7)
        visit.so_section_id.sequence = 1
        sol1.sequence = 2
        sol2.sequence = 3

        so.action_confirm()

        visit_task = visit.task_id
        self.assertEqual(sol1.task_id.allocated_hours, 4.0)
        self.assertEqual(sol2.task_id.allocated_hours, 4.0)
        self.assertEqual(visit_task.allocated_hours, 8.0)

    def test_adding_visit_creates_one_sale_order_line(self):
        self._generate_partner()
        so = self._generate_sale_order()
        self._generate_sale_order_line(sale_order=so)
        self._generate_sale_order_line(sale_order=so)

        self._generate_visit(sale_order=so)

        self.assertEqual(len(so.order_line), 3)

    def test_marking_visit_task_done_completes_descendants(self):
        (
            so,
            visit,
            sol1,
            sol2,
        ) = self._generate_so_with_one_visit_two_lines_and_descendants()
        so.action_confirm()
        parent = visit.task_id

        parent.action_fsm_validate()

        self._assert_is_done(parent)

    def _assert_is_done(self, task):
        """Recursively assert all tasks in a hierarchy are complete"""
        self.assertTrue(task.is_closed)
        for child in task.child_ids:
            self._assert_is_done(child)

    def test_marking_visit_task_done_does_not_create_sale_order_line(self):
        so, visit, sol1, sol2 = self._generate_so_with_one_visit_two_lines()
        so.action_confirm()

        visit.task_id.action_fsm_validate()

        self.assertEqual(len(so.order_line), 3)

    def test_confirming_so_names_visit_properly(self):
        """Visits should be named <SO NUMBER> - Visit <visit #> - <visit label>"""
        so, visit, sol1, sol2 = self._generate_so_with_one_visit_two_lines()
        so.name = "SO12345"
        so.action_confirm()
        task = visit.task_id

        supposed_name = "SVR12345-1 - Test Company - Test Label"
        self.assertEqual(task.name, supposed_name)
