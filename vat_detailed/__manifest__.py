{
	'name': 'Vat Detailed', 
	'license': 'LGPL-3',
    'version': '0.1',

	'description': 'For Vat Detailed', 
	
	'author': 'Rana Rizwan',
	
	'depends': [
	'base',
	'sale',
	'travel_package',
	'account',
	'hr',
	'report_xlsx'
	], 
	
	'data': [
		'template.xml',
		"security/security.xml",
		"security/ir.model.access.csv",
	],
}