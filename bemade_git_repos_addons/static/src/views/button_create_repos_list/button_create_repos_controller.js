/** @odoo-module */

import { useService } from "@web/core/utils/hooks";
import { ListController } from "@web/views/list/list_controller";

export class ButtonCreateReposController extends ListController {
	setup() {
		super.setup();
		this.orm = useService("orm");
	}

	async onCreateRepos() {
        this.actionService.doAction({
            type: 'ir.actions.act_window',
            res_model: 'git.repos.wizard',  // Replace 'your.wizard.model' with the model of your wizard
            views: [[false, 'form']],
            target: 'new',
        });
	}

}
