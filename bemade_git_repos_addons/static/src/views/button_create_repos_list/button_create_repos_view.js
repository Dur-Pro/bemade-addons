/** @odoo-module */

import { listView } from "@web/views/list/list_view";
import { registry } from "@web/core/registry";
import { ButtonCreateReposController as Controller } from './button_create_repos_controller';

export const ButtonCreateReposView = {
    ...listView,
    Controller,
    buttonTemplate: 'bemade_git_repos_addons.ButtonCreateReposView.Buttons',
};

registry.category("views").add("button_create_repos", ButtonCreateReposView);
