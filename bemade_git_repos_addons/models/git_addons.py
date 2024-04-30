from odoo import api, fields, models
import os


class GitAddons(models.Model):
    _name = 'git.addons'
    _description = 'Git Addons'

    name = fields.Char(string='Addon Name')
    branch_id = fields.Many2one('git.branch', string='Branch')

    @api.model
    def get_addons(self):
        self.search([]).unlink()  # Remove old records
        branches = self.env['git.branch'].search([])
        for branch in branches:
            repos = branch.repos
            addons_path = repos.addons_path
            if os.path.isdir(addons_path):
                addons = next(os.walk(addons_path))[1]
                for addon in addons:
                    self.create({
                        'name': addon,
                        'branch_id': branch.id,
                    })

    def action_update_addons(self):
        self.get_addons()
