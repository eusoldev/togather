# -*- coding: utf-8 -*-
{
    # Application Information
    'name' : 'Quotation Builder Report',
    'license': 'LGPL-3',
    'version': '0.1',
    # 'category' : 'Sales',
    'description' : """ 
        Quotation Builder Report
    """,
    'summary' : """
        Quotation Builder Report
    """,
    
    # Author Information
    'author' : 'Odoo.',
    'maintainer': 'eusol',  
    'website': 'eusol.net',
    
    # Technical Information
    'depends': ['base','quotation_builder'],
    'data': [
            'views/template.xml',
            'views/module_report.xml'
            ],
    'fonts': [
    'static/src/fonts/NafeesNastaleeq.eot?#iefix',
    'static/src/fonts/NafeesNastaleeq.woff',
    'static/src/fonts/NafeesNastaleeq.ttf',
    'static/src/fonts/NafeesNastaleeq.svg#NafeesNastaleeq'
    ],
    
    'css': ['static/src/fonts/styles.css'],
    # App Technical Information
    'installable': True,
    'auto_install': False,
    'application' : True,
    'active': True,
}