# -*- coding: utf-8 -*-
{
    # Application Information
    'name' : 'Voucher Report',
    'license': 'LGPL-3',
    'version': '0.1',
    # 'category' : 'Sales',
    'description' : """ 
        Voucher Report
    """,
    'summary' : """
        Voucher Report
    """,
    
    # Author Information
    'author' : 'EUSOL',
    'maintainer': 'EUSOL',  
    'website': 'eusol.net',
    
    # Technical Information
    'depends': ['base','sale'],
    'data': [
            'views/template.xml',
            'views/module_report.xml'
            ],
    
    # App Technical Information
    'installable': True,
    'auto_install': False,
    'application' : True,
    'active': True,
}