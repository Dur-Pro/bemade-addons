from odoo import models, fields, api, exceptions


class GitRepos(models.Model):
    _name = 'git.repos'
    _description = 'Git Repositories'

    name = fields.Char(string='Name', required=True)
    url = fields.Char(string='URL')
    branches = fields.One2many('git.branch', 'repo_id', string='Branches', readonly=True)
    active_branch = fields.Many2one('git.branch', string='Active Branch')

    @api.onchange('url')
    def _check_repo(self):
        self.branches = [(5, 0, 0)]  # clear existing branches
        try:
            branches_list = self.get_branches(self.url)  # a function you need to implement to get branches from git
            for branch in branches_list:
                self.env['git.branch'].create({
                    'name': branch,
                    'repo_id': self.id
                })
        except:
            return {
                'warning': {
                    'title': "URL validation",
                    'message': "The URL is not valid or the repository is not accessible.",
                },
            }

    @api.model
    def get_branches(self, url):
        try:
            repo = Repo.clone_from(url, '/tmp/repo')  # clone repository to a temp folder
            branches = [str(branch) for branch in repo.branches]
            return branches
        except Exception as e:
            # Log the error and return an empty list or handle the exception
            return []

    @api.model
    def action_create_repo(self, vals_list=None):
        """
        This method will be called from button that we have created using owl js
        """
        if not vals_list:
            vals_list = [{'name': 'Test Repo', 'url': 'http://example.com', 'active_branch': 'master'}]
        repo = self.create(vals_list)
        return repo

    @api.model
    def action_clone_repos(self):
        try:
            # Choose active branch
            repo = Repo('/tmp/repos/' + self.name)
            repo.git.checkout(self.active_branch.name)
        except Exception as e:
            # Log the error and handle the exception appropriately
            pass

    @api.model
    def action_switch_branch(self, branch_id):
        try:
            # Choose a branch
            repo = Repo('/tmp/repos/' + self.name)
            repo.git.checkout(branch_id)
            # Update active_branch field
            self.active_branch = self.env['git.branch'].browse(branch_id)
        except Exception as e:
            # Log the error and handle the exception appropriately
            pass

    @api.model
    def action_update_repos(self):
        self._check_repo()

    @api.model
    def action_delete_repos(self):
        # Delete the physical directory '/tmp/repos/'+self.name
        # There is a lot of ways to do this. Here is one:
        import shutil
        shutil.rmtree('/tmp/repos/' + self.name)
        # Delete the DB record
        self.unlink()