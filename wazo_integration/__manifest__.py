{
    'name': 'Wazo Configurator',
    'version': '17.0.0.1.0',
    'summary': 'Module to configure Wazo server from Odoo',
    'category': 'Tools',
    'author': 'Benoît Vézina',
    'website': 'http://www.bemade.org',
    'license': 'OPL-1',
    'depends': [
        'base',
        'hr'
    ],
    'data': [
        'views/res_config_settings_views.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
