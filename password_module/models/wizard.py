# #-*- coding:utf-8 -*-
from odoo import api, models, fields,_
from odoo.exceptions import ValidationError, UserError
import passlib.context

from odoo.http import request



DEFAULT_CRYPT_CONTEXT = passlib.context.CryptContext(
	# kdf which can be verified by the context. The default encryption kdf is
	# the first of the list
	['pbkdf2_sha512', 'plaintext'],
	# deprecated algorithms are still verified as usual, but ``needs_update``
	# will indicate that the stored hash should be replaced by a more recent
	# algorithm. Passlib 1.6 supports an `auto` value which deprecates any
	# algorithm but the default, but Ubuntu LTS only provides 1.5 so far.
	deprecated=['plaintext'],
)



class custom_password_confimations(models.TransientModel):
	_name = "password.confirmations"
	_description = 'Password Confirmations'

	current_user = fields.Many2one('res.users', string='User',default=lambda self: self.env.user)

	get_password = fields.Char('Password')




	def _crypt_context(self):

		""" Passlib CryptContext instance used to encrypt and verify
		passwords. Can be overridden if technical, legal or political matters
		require different kdfs than the provided default.

		Requires a CryptContext as deprecation and upgrade notices are used
		internally
		"""
		return DEFAULT_CRYPT_CONTEXT




	def get_password_confirmations(self):

		if self.get_password:

			
			self.env.cr.execute(
				"SELECT COALESCE(password, '') FROM res_users WHERE id=%s",
				[self.current_user.id]
			)


			[hashed] = self.env.cr.fetchone()

			valid, replacement = self._crypt_context()\
				.verify_and_update(self.get_password, hashed)


			if valid == True:

				menu_id = self.env.ref('password_module.password_menu').id
				action_against_menu_id = self.env.ref('password_module.action_password_work').id


				# record_url = "/web#id=" + str(self.id) + "&view_type=list&model=password.module&menu_id="+str(menu_id)+"&action="+str(action_against_menu_id)
				record_url = "/web#view_type=list&model=password.module&menu_id="+str(menu_id)+"&action="+str(action_against_menu_id)



				return {

					'name': _("Password Management"),
					'type':'ir.actions.act_url',
					'target':'self',
					'url':record_url

				}


			if valid == False:
				raise ValidationError('Wrong Account Password!')


		else:
			raise ValidationError('Please Enter Your Account Password!')




	def cancel_form_now(self):

		return {
			'type': 'ir.actions.act_url',
			'url': '/web',
			'target': 'self'
		}