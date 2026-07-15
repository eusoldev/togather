from odoo import models, fields, api,_

from datetime import datetime

from odoo import models, fields, api,_
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo.exceptions import ValidationError, UserError
from dateutil.parser import parse
from jinja2 import Environment, BaseLoader
from odoo.http import request
from odoo.tools import html2plaintext
import binascii
import base64
import qrcode
from io import BytesIO
import codecs
import uuid
from markupsafe import escape

class reservation_link(models.Model):
	_name = 'quotation.builder.link'
	_description = 'Reservation Link Wizard'
	reservation_link_ref = fields.Char(string='Quotation Ref')
	resvartion_link_id = fields.Char(string='ID')
	reservation_link_email = fields.Char(string='Email')
	reservation_link = fields.Char(string='Quotation Link')

	def send_reservation_email_to_customer(self,**opt):
		sale_getting = self.env['reservation.order'].sudo().search([('id','=',self.resvartion_link_id)])
		current_user = escape(self.env.user.name or '')
		current_links = escape(self.reservation_link or '')
		body = (
			"<p>Quotation Builder Link Has Been Created By %s</p>"
			'<p><a href="%s" target="_blank" rel="noopener noreferrer">%s</a></p>'
		) % (current_user, current_links, current_links)
		if sale_getting:

			sale_getting.message_post(body=body,subject="Pressing Quotation Builder Button")
		sale_order = self.env['reservation.order'].sudo().search([('id', '=', int(self.resvartion_link_id))])
		email_from = self.env['ir.mail_server'].sudo().search([] , limit=1)
		for rec in sale_order:
			if rec.partner_id:

				if rec.partner_id.email:
					mail_obj = self.env['mail.mail']
					send_to = "{0}".format(rec.partner_id.email)
					
					company_list = []
					for z in rec.company_id:
						company_list.append(z)

					partner_list = []
					for z in rec.partner_id:
						partner_list.append(z)

					sale_person=[]
					if rec.partner_id:
						sale_person.append(self.env.user.name)

					reservation_list=[]
					if self.reservation_link:
						reservation_list.append(self.reservation_link)
					form_design = """

					<div style="width:100%";>

					<div style="width:100%; text-align:center;">
					<img src="https://i.ibb.co/rGgQSfp/unnamed.png" style="width:100px;" />
					</div> 
						<br/>   
						<br/>
						 <span style="font-size: 17px; font-weight:bold;color: black;">From</span> :   
						 {%for person in sale_person%}
							<span style="font-size: 17px; font-weight:normal;color: black;">{{person}}</span>
						{%endfor%}
						<br/>
						<span style="font-size: 17px; font-weight:bold;color: black;">Dear</span>
                        {%for partner in partner_list%}
                            <span style="font-size: 17px; font-weight:normal;color: black;">{{partner.name}}</span>
                        {%endfor%},
						<br/>
						<div>
						<h4 style="margin-top:10px;">
						<b style="color: black;">Click On The Link To See the Quotation Details:</b> 
					</h4>
					<h4 style="margin-top:10px;">

					 {%for link in reservation_list%}
							<a  href="{{link}}"> {{link}}</a>
					{%endfor%}

					</h4>

					</div>
						<br/>
						<br/>
						<b>Regards:</b>
						<br/>
						Togather Travel
						<br/>

						<br/>

						<div class="custom_footer" style="width:100%;">

						</div>
						</div>

					"""
					
					template = Environment(loader=BaseLoader).from_string(form_design)
					template_vars = {"company_list": company_list,"reservation_list": reservation_list,"sale_person": sale_person,"partner_list":partner_list}
					html_out = template.render(template_vars)
					my_mail =  mail_obj.sudo().create({
					'email_from': email_from.smtp_user,
					'email_to': send_to,
					'subject': "Quotation Custom Link ",
					'body_html':
					'''<span  style="font-size: 14px"><br/>
					  <br/>%s </span> 
					  <br/><br/>''' % (html_out)}).sudo().send()