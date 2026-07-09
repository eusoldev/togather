# -*- coding: utf-8 -*-
{
    # Application Information
    'name' : 'Offers Builder Report',
    'version': '0.1',
    'license': 'LGPL-3',
    # 'category' : 'Sales',
    'description' : """ 
        Offers Builder Report
    """,
    'summary' : """
        Offers Builder Report
    """,
    
    # Author Information
    'author' : 'Rana Rizwan',
    'maintainer': 'EUSOl',  
    
    # Technical Information
    'depends': ['base','offers_builder'],
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