#
#    Bemade Inc.
#
#    Copyright (C) September 2023 Bemade Inc. (<https://www.bemade.org>).
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
    'name': 'Project Documents',
    'version': '15.0.1.0.0',
    'summary': 'Improved workflow for project documents.',
    'description': """Adds multiple workflow items to project documents, including:
                        * Approval stages
                        * Document versions with revision numbers
                        * Ability to request document approval from a partner
                    """,
    'category': '',
    'author': 'Bemade Inc.',
    'website': 'https://www.bemade.org',
    'license': 'OPL-1',
    'depends': ['documents',
                'bemade_documents_portal',
                'documents_project',
                ],
    'data': ['views/project_views.xml',
             'wizard/request_approvals_wizard.xml',
             'security/ir.model.access.csv',
             ],
    'assets': {
        'web.assets_backend': [
            'bemade_project_documents/static/src/js/documents_controller_patch.js'
        ],
        'web.assets_qweb': [
            'bemade_project_documents/static/src/xml/documents_views.xml'
        ]
    },
    'installable': True,
    'auto_install': False,
}