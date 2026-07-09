# -*- coding: utf-8 -*-
{
    'name': "Email templates",

    'summary': """ """,

    'description': """
        To create multiple email templates
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
    ],
}
