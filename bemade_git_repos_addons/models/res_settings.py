from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'Directory Settings'

    clone_dir = fields.Char(string='Clone Directory')
    addons_dir = fields.Char(string='Addons Directory')


    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)

        addons_dir = self.env['ir.config_parameter'].get_param('bemade_git_repos_addons.addons_dir')
        clone_dir = self.env['ir.config_parameter'].get_param('bemade_git_repos_addons.clone_dir')

        if 'addons_dir' in fields and addons_dir:
            res['addons_dir'] = addons_dir
        if 'clone_dir' in fields and clone_dir:
            res['clone_dir'] = clone_dir
        return res