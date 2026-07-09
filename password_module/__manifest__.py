# -*- coding: utf-8 -*-
{
    'name': "Password Management",

    'summary': """
        Password Management""",

    'description': """
        Password Management
    """,

    'author': "Eusol",
    'website': "https://contact.fyi/rylctcvsju",

    # for the full list
    'category': 'Uncategorized',
    'license': 'LGPL-3',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','web'],

    # always loaded
    'data': [
        'security/security_group.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/password_confirmations.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'password_module/static/src/js/app.js',
            'password_module/static/src/xml/password_action_template.xml',
        ],
    },
}
