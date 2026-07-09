from odoo import models, fields, api
from odoo.exceptions import ValidationError

class custom_Email(models.Model):
	_name = 'custom.email'
	_description = 'Email template'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_rec_name = 'name'

	name = fields.Char(required=True, copy=False)
	body_arch = fields.Html(string='Body', translate=False)
	body_html = fields.Html(string='Body converted to be send by mail', sanitize_attributes=False)


	def write(self, vals):
	    self.message_post(body="Record has been modified by:<strong> %s </strong>" %(self.env.user.name))
	    res = super(custom_Email, self).write(vals)
	    return res

	


