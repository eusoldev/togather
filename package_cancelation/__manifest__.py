# -*- coding: utf-8 -*-
{
    'name': "Package Cancelation",

    'summary': """
        Package Cancelation""",

    'description': """
        Package Cancelation
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'license': 'LGPL-3',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','travel_package'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/cancelation_views.xml',
    ],
}
