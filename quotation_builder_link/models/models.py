# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api,_
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo.exceptions import ValidationError, UserError

from odoo.http import request
import uuid
from dateutil.parser import parse
from jinja2 import Environment, BaseLoader
from odoo.tools import html2plaintext
import binascii
import base64
import qrcode
from io import BytesIO
import codecs



class reservation_link(models.Model):
	_inherit = 'sale.order'
	_description = 'reservation_link.reservation_link'

	customer_note = fields.Text("Customer Note", tracking=True)

	def _portal_ensure_token_reservation_link(self):
		return str(uuid.uuid4())

	def get_reservation_link_url(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):

		url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')+'/quotation_builder_link_web_view/' + '%s'%str(self.id)  +'%s?access_token=%s%s%s%s%s' % (
			suffix if suffix else '',
			self._portal_ensure_token_reservation_link(),
			'&report_type=%s' % report_type if report_type else '',
			'&download=true' if download else '',
			query_string if query_string else '',
			'#%s' % anchor if anchor else ''
		)


		return url


	def reservation_button_link(self):
		reservation_ref = ''
		reservation_links = ''
		if self.partner_id.email:
			reservation_ref = self.name
			in_email = self.partner_id.email
			reservation_id = self.id
			reservation_links = self.get_reservation_link_url()
		else:
			raise ValidationError('This Partner Has No Email, Please Add The Email First!')
		return {
		'res_model': 'quotation.builder.link',
		'type': 'ir.actions.act_window',
		'view_mode': 'form',
		'name':'Quotation Builder Link',
		'view_type': 'form',
		'target': 'new',
		'context': dict(
			default_reservation_link_ref=reservation_ref,
			default_resvartion_link_id=reservation_id,
			default_reservation_link_email=in_email,
			default_reservation_link=reservation_links,
			),
		
		 }

class allservices_ext(models.Model):
	_inherit = 'all.services'
	_description = 'all_services.all_services'


	image_url = fields.Char(string="Image Url For Reservation")