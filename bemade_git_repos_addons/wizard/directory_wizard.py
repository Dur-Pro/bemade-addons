from odoo import models, fields, api
import os


class DirectoryWizard(models.TransientModel):
    _name = 'directory.wizard'
    _description = 'Directory Wizard'

    # Directories to exclude from the list, including hidden directories and directories that are not relevant
    EXCLUDED_DIRS = [
        '.idea',
        '.cache',
        '.config',
        '.git',
        '.local',
        '.odoo-deploy',
        '.ssh',
        '.testing',
        'conf',
        'design-themes',
        'enterprise',
        'filestore',
        'Notes',
        'odoo',
        'server',
        'themes',
        'tools',
        'venv',
    ]

    def _get_directory_list(self):
        # Fetch all directories in the current working directory
        directories = [(d, d) for d in os.listdir(os.getcwd())
                       if os.path.isdir(d) and d not in self.EXCLUDED_DIRS]
        return directories

    addons_dir = fields.Selection(_get_directory_list, string='Addons Directory')
    repos_dir = fields.Selection(_get_directory_list, string='Repos Directory')
    new_directory = fields.Char(string='New Directory')

    def create_directory(self):
        for record in self:
            if not os.path.exists(record.new_directory):
                os.makedirs(record.new_directory)
                wizard = self.create({'new_directory': False})  # reset the value of new_directory
                return {
                    'name': 'Directory Wizard',
                    'res_model': self._name,
                    'res_id': wizard.id,
                    'views': [(False, 'form')],
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }
            else:
                return {
                    'warning': {
                        'title': "Directory Exists",
                        'message': "The directory already exists, please choose another name or directory.",
                    }
                }

    def apply_selections(self):
        IrConfigParameter = self.env['ir.config_parameter']

        if self.addons_dir:
            IrConfigParameter.set_param('bemade_git_repos_addons.addons_dir', self.addons_dir)
        if self.repos_dir:
            IrConfigParameter.set_param('bemade_git_repos_addons.clone_dir', self.repos_dir)

        return {}

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)

        addons_dir = self.env['ir.config_parameter'].get_param('bemade_git_repos_addons.addons_dir')
        repos_dir = self.env['ir.config_parameter'].get_param('bemade_git_repos_addons.clone_dir')

        if 'addons_dir' in fields and addons_dir:
            res['addons_dir'] = addons_dir
        if 'repos_dir' in fields and repos_dir:
            res['repos_dir'] = repos_dir
        return res