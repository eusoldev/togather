{
	'name': 'Travel Package  ', 

	'description': 'travel Package', 
	'license': 'LGPL-3',
	'author': 'EUSOL',
	'version': '0.1',
	
	'depends': [
	'base',
	'mail',
	'account',
	'mass_mailing',
	'res_partner_ext',
	# 'add_voucher_report',
	'crm',
	
	], 
	'data': [
		"security/security.xml",
		'views/email_templates.xml',
		"security/ir.model.access.csv",
		'views/template.xml',
		'views/account_move.xml',
		'views/payment_ext.xml',
		'views/res_partner.xml',
		'views/menu_items.xml',
		'views/mailing_template.xml',
		'data/data.xml',
	],
	'assets': {
		'web.assets_backend': [
			'travel_package/static/src/js/form_compiler_patch.js',
		],
	},
}