from odoo import models, fields


class GitBranch(models.Model):
    _name = 'git.branch'
    _description = 'Git Branch'

    name = fields.Char(string='Branch Name', required=True)
    repo_id = fields.Many2one('git.repos', string='Repository')
    active = fields.Boolean(string='Active', default=False)
    branch_addons = fields.One2many(
        comodel_name='git.addons',
        inverse_name='branch_id',
        string='Addons',
        readonly=True)


    # If there are additional fields or relations you need, please define them here