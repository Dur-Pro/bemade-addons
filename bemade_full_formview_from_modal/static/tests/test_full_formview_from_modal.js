/** @odoo-module **/

import { registry } from "@web/core/registry";
import { stepUtils } from "@web_tour/tour_service/tour_utils";

registry.category("web_tour.tours").add("full_formview_from_modal_tour", {
    test: true,
    url: '/web',
    steps: () => [stepUtils.showAppsMenuItem(),
        {
            content: 'Go to contacts',
            trigger: '.o_app[data-menu-xmlid="contacts.menu_contacts"]',
        },
        {
            content: 'Click search',
            trigger: '.o_searchview_input',
        },
        {
            content: 'insert text in the search bar',
            trigger: '.o_searchview_input',
            run: 'text Test parent',
        },
        {
            content: 'Validate search',
            trigger: '.o_searchview_autocomplete .o_menu_item:contains("Name")',
        },
        {
            content: 'Open the contact',
            trigger: '.o_kanban_record .o_kanban_record_title span:contains("Test parent")',
        },
        {
            content: 'Open the child',
            trigger: 'div[name="child_ids"] .o_kanban_record:first-child',
        },
        {
            "trigger": "button:contains('Open')",
            "content": "Click the open button on the modal",
            "run": "click",
        },
        {
            content: 'Make sure the form view opens to Test Child',
            trigger: 'div.o_last_breadcrumb_item span:contains("Test Child")',
        }
    ]
});
