{
    'name': "Custom Sales Report",
    'description': "Custom Sales Report",
    'author': 'EUSOL',
    'website': "http://www.eusol.net",
    'category': 'sale',
    'license': 'LGPL-3',
    'version': '0.1',
    'application': True,
    'depends': ['base','hr','travel_package'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'template.xml',
        'views/module_report.xml',
    ],
}