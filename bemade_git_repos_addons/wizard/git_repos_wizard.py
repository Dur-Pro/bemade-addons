from odoo import models, fields


class GitReposWizard(models.TransientModel):
    _name = 'git.repos.wizard'
    _description = 'Git Repos Wizard'

    url = fields.Char(string='Repository URL', required=True, help='URL of the git repository you want to clone')
    branch_id = fields.Many2one('git.branch', 'Active Branch')

    def get_repo_branches(self):
        self.ensure_one()

        # code for pulling branch list from git repo using `self.url`
        # here the git branch data should be transformed into {'name': 'branch_name'} form
        branches_datum = [{'name': 'branch_name'}]

        # logic for checking if repo can be reach and have branches
        if not branches_datum:
            raise exceptions.ValidationError('The Repository URL is not accurate or The repository has no branches.')

        # create git.branch records or link with existing ones
        for branch_data in branches_datum:


    # def action_confirm(self):
    #     self.ensure_one()
    #
    #     # Perform the git clone operation
    #     # Be careful, errors should be managed
    #     try:
    #         git.Repo.clone_from(self.url, self.clone_dir)
    #     except Exception as e:
    #         raise Warning(str(e))
    #
    #     return {'type': 'ir.actions.act_window_close'}