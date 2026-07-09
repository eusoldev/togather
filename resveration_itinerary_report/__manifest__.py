# -*- coding: utf-8 -*-
{
    # Application Information
    'name' : 'Itinerary Report',
    'license': 'LGPL-3',
    'version': '0.1',
    # 'category' : 'Sales',
    'description' : """ 
        Itinerary Report
    """,
    'summary' : """
        Itinerary Report
    """,
    
    # Author Information
    'author' : 'Odoo.',
    'maintainer': 'eusol',  
    'website': 'eusol.net',
    
    # Technical Information
    'depends': ['base','web','sale'],
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