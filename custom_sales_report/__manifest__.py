{
    'name': "Employee Performance Report",
    'description': "Employee Performance Report",
    'author': 'EUSOL',
    'website': "http://www.eusol.net",
    'category': 'sale',
    'license': 'LGPL-3',
    'version': '0.1',
    'application': True,
    'depends': ['base','hr','report_xlsx','travel_package'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'template.xml',
        'views/module_report.xml',
    ],
}