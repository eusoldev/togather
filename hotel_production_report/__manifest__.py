{
    'name': "Hotel Production Report",
    'description': "Hotel Production Report",
    'author': 'EUSOL',
    'website': "http://www.eusol.net",
    'category': 'sale',
    'version': '0.1',
    'license': 'LGPL-3',
    'application': True,
    'depends': ['base','report_xlsx','travel_package'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'template.xml',
        'views/module_report.xml',
    ],
}
