

from odoo import models, fields, api


class password_module(models.Model):
	_name = 'password.module'
	_description = 'Password Module'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_rec_name = 'name'

	name = fields.Char(required=True, copy=False, index=True)
	current_user = fields.Many2one('res.users', string='User',default=lambda self: self.env.user)
	create_date = fields.Date(default=fields.Date.today(), required=True )
	color = fields.Integer()
	tree_link_id = fields.One2many('password.lines', 'password_id')
	



class PasswordLines(models.Model):
	_name = 'password.lines'
	_description = 'Password Lines'

	name = fields.Char('Description', index=True)
	account_id = fields.Char( string='Email')
	norm_password = fields.Char(string='Password')
	link = fields.Char(string='Website Link')
	password_id = fields.Many2one('password.module')


