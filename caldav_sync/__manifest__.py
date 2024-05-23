#
#    Bemade Inc.
#
#    Copyright (C) 2023-June Bemade Inc. (<https://www.bemade.org>).
#    Author: Marc Durepos (Contact : mdurepos@durpro.com)
#
#    This program is under the terms of the GNU Lesser General Public License (LGPL-3)
#    For details, visit https://www.gnu.org/licenses/lgpl-3.0.en.html

{
    'name': 'CalDAV Sync',
    'version': '1.0',
    'category': 'Calendar',
    'summary': 'Synchronize Odoo Calendar with a CalDAV Server',
    'description': """
        This module allows Odoo to synchronize calendar events with a CalDAV server.
    """,
    'author': 'Your Name',
    'depends': ['base', 'calendar'],
    'data': [
        'data/caldav_sync_data.xml',
    ],
    'installable': True,
    'application': True,
}
