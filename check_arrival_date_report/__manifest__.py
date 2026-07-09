{
    'name': "Check Arrival Date Report",
    'description': "Check Arrival Date Report",
    'author': 'Raan Rizwan',
    'website': "http://www.odoo.com",
    'category': 'sale',
    'license': 'LGPL-3',
    'version': '0.1',
    'application': True,
    'depends': ['base','report_xlsx'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'template.xml',
        'views/module_report.xml',
    ],
}