# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import datetime
import logging
import psycopg2
import smtplib
import threading
import re

from collections import defaultdict

from odoo import _, api, fields, models
from odoo import tools
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)




class MailMessage(models.Model):

	_inherit = "mail.message"


	@api.model_create_multi
	def create(self, values_list):
		server_resrv_1 = self.env['ir.mail_server'].sudo().search([('id','=',1)] , limit=1)
		server_team_2 = self.env['ir.mail_server'].sudo().search([('id','=',4)] , limit=1)
		# if not vals.get("mail_server_id"):

		models_predined = ['reservation.order','all.services','account.move','quotation.builder','account.payment','add.hyperpay_wizard.model']
		
		subject_hyperpay = re.compile (r'Hyperpay')


		for vals in values_list:
			if vals.get("model") in models_predined:
				vals["mail_server_id"] = server_resrv_1.id
				vals["email_from"] = '"{0}" <{1}>'.format(str(self.env.user.name),str(server_resrv_1.smtp_user))

			elif vals.get('subject'):
				results_hyperpay = subject_hyperpay.search(vals.get("subject"))
				if results_hyperpay != None:
					if results_hyperpay.group() == 'Hyperpay':
						vals["mail_server_id"] = server_resrv_1.id
						vals["email_from"] = '"{0}" <{1}>'.format(str(self.env.user.name),str(server_resrv_1.smtp_user))
				else:
					vals["mail_server_id"] = server_team_2.id
					vals["email_from"] = '"{0}" <{1}>'.format(str(self.env.user.name),str(server_team_2.smtp_user))
			
			else:
				vals["mail_server_id"] = server_team_2.id
				vals["email_from"] = '"{0}" <{1}>'.format(str(self.env.user.name),str(server_team_2.smtp_user))





		return super(MailMessage, self).create(values_list)