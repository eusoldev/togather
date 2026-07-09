# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.tools.misc import formatLang, format_date, get_lang


class AddVoucherReport(models.Model):
	_inherit = 'account.move'

	def action_invoice_sent(self):
		""" Open a window to compose an email, with the edi invoice template
			message loaded by default
		"""
		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		template = ir_model_data._xmlid_lookup('account.email_template_edi_invoice')[1]
		voucher_template = ir_model_data._xmlid_lookup('add_voucher_report.add_voucher_email_template')[1]
		# lang = get_lang(self.env)
		
		if voucher_template:
			so_id = self.env['reservation.order'].search([('name','=',self.package_no)],limit=1)
			# lang_voucher = voucher_template._render_template(voucher_template, 'reservation.order', so_id.id)
		# else:
		# 	lang = lang.code

		compose_form = ir_model_data._xmlid_lookup('account.account_move_send_wizard_form')[1]
		# template_list = [template.ids, voucher_template.ids]
		ctx = dict(
			default_model='account.move',
			default_res_ids=self.ids,
			default_res_model='account.move',
			default_use_template=bool(template),
			default_template_id=template ,
			default_composition_mode='comment',
			mark_invoice_as_sent=True,
			# attachment_ids= [(6,0,template_list)],
			custom_layout="mail.mail_notification_paynow",
			# model_description=self.with_context(lang=lang).type_name,
			force_email=True
		)
		print (ctx)
		return {
			'name': _('Send Invoice'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'account.invoice.send',
			'views': [(compose_form, 'form')],
			'view_id': compose_form,
			'target': 'new',
			'context': ctx,
		}

