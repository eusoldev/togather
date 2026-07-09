{
	'name': 'Contracts', 

	'description': 'For Create Outsource Service Contract',
	'license': 'LGPL-3',
    'version': '0.1', 
	
	'author': 'Abdurrehman Khalil , Enterprise Cube.',
	
	'depends': [
	'base',
	'sale',
	'travel_package',
	], 
	
	'data': [
		'template.xml',
		"security/security.xml",
		"security/ir.model.access.csv",
	],
}