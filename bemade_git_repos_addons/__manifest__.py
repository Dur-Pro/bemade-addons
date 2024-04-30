#
#    Bemade Inc.
#
#    Copyright (C) July 2023 Bemade Inc. (<https://www.bemade.org>).
#    Author: Marc Durepos (Contact : marc@bemade.org)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
{
    'name': 'Bemade Addons from Git Repositories',
    'version': '17.0.1.0.0',
    'summary': 'A way to install addons from git repositories.',
    'description': """
    This module allows you to install addons from git repositories.
    
    Configuration:
    
    Set the directory where the repository will be cloned and the directory where the activated addons are located.
    
    
    Usage:
    
    You can add a git repository in the Apps application and then enabled the addons from it.
    
    In the Apps application, you will see a new option to add git repositories.
    This will allow you to select the repository and the branch you want to install.
    
    You can then navigate to apps and in the menu, you will see a new option to enabled addons from git repositories.
    """,
    'category': 'Generic Modules/Others',
    'author': 'Bemade Inc.',
    'website': 'https://www.bemade.org',
    'license': 'OPL-1',
    'depends': [
        'base_import_module'
    ],
    'data': [
        # 'data/default_directories_data.xml',
        'security/ir.model.access.csv',
        'views/git_repos_views.xml',
        'views/res_settings_views.xml',
        'views/action_and_menu.xml',
        'wizard/directory_wizard_views.xml',
        'wizard/git_repos_wizard_views.xml',
    ],    'demo': [],
    'assets': {
        'web.assets_backend': [
            '/bemade_git_repos_addons/static/src/views/*/*',
        ],
    },
    'installable': True,
    'auto_install': False,
}
