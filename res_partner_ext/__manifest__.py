# -*- coding: utf-8 -*-
{
    'name': "Partner Extension",

    'summary': """
        Partner Extension""",

    'description': """
        Partner Extension
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': [
    'base',
    'mass_mailing',
    # 'hr_timesheet',
    # 'base_geolocalize',
    # 'project',
    # 'purchase',
    # 'hr_recruitment',
    # 'event',
    # 'hr_payroll_community',
    # 'hr_expense',
    # 'hr_resignation',
    # 'hr',
    # 'hr_attendance',
    'account',
    'crm',
    'sales_team',
    'sale',
    # 'hr_holidays',
    'contacts',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/partner_view.xml',
    ],
}
