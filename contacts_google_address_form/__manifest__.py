# -*- coding: utf-8 -*-
{
    'name': 'Contact Google Address Form',
    'version': '19.0.1.0.0',
    'author': 'Ayyan Saddiqui',
    'license': 'AGPL-3',
    'maintainer': 'Ayyan Saddiqui<ayyansaddiqui420@gmail.com>',
    'support': 'ayyansaddiqui420@gmail.com',
    'category': 'Base',
    'sequence': 1000,
    'description': """
Contact Google Address Form
===========================

Use Google Address Form autocomplete to help you find address
""",
    'depends': [
        'base_geolocalize',
        'web_google_maps',
    ],
    'website': 'https://github.com/ayyan420',
    'data': [
        'views/res_partner.xml',
    ],
    'demo': [],
    'installable': True
}
