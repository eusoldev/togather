# -*- coding: utf-8 -*-
{
    'name': "Customizing The Odoo Survey Module",

    'summary': """
             This is for Customizing The Odoo Survey Module
                """,

    'description': """
       This is for Customizing The Odoo Survey Module
    """,

    'author': "Ayyan",
    'website': "http://www.eusol.net",

    'category': 'Uncategorized',
    'license': 'LGPL-3',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','survey','mail'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/templates.xml',
    ],
}
