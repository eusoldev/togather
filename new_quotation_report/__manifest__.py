# -*- coding: utf-8 -*-
{
    # Application Information
    'name' : 'New Quotation Report',
    'license': 'LGPL-3',
    'version': '0.1',
    'description' : """ 
        New Quotation Report
    """,
    'summary' : """
        New Quotation Report
    """,
    
    # Author Information
    'author' : 'EUSOL.',
    'maintainer': 'EUSOL',  
    'website': 'eusol.net',
    
    # Technical Information
    'depends': ['base','web','quotation_builder'],
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