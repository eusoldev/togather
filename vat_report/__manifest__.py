{
    'name': "Vat Report",
    'description': "Vat Report",
    'author': 'Raan Rizwan',
    'website': "http://www.eusol.net",
    'category': 'sale',
    'license': 'LGPL-3',
    'version': '0.1',
    'application': True,
    'depends': ['base','account','report_xlsx'],
    'data': [
        'template.xml',
        'views/module_report.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
}