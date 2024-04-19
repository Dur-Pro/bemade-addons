{
    'name': 'Bemade PWA Configuration',
    'version': '1.0',
    'summary': 'Manage PWA settings including dynamic app icons',
    'description': """
Manage Progressive Web App Settings
===================================
This module allows administrators to configure Progressive Web App (PWA) settings directly from Odoo's interface. 
This includes setting color uploading app icons, and dynamically generating icons of different sizes to be used in the 
web manifest per company.
""",
    'author': 'Benoît Vézina',
    'website': 'https://www.bemade.com',
    'category': 'Tools',
    'license': 'OPL-1',
    'depends': ['web'],
    'data': [
        'views/res_config_settings_views.xml',
        # 'security/ir.model.access.csv',
    ],
    'demo': [
        # List any demo data files here
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
