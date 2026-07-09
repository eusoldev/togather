from datetime import datetime
from odoo import models, fields, tools,api,_
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
from dateutil.parser import parse
from jinja2 import Environment, BaseLoader

class Inheirt_surveeys_inoputs(models.Model):
	_inherit = 'survey.user_input'
	partner_id = fields.Many2one('res.partner', string='Partner', readonly=True , store=True , compute="get_partners_in_inpoits")
	@api.depends('user_input_line_ids')
	def get_partners_in_inpoits(self):
		if self.user_input_line_ids:
			for x in self.user_input_line_ids:
				if x.question_id.title == 'What is your Email?':
					get_email = x.value_text
					self.partner_id = self.env['res.partner'].search([('email','=',get_email),('b2c_customer','!=',False)] , limit=1)
					self.email = self.env['res.partner'].search([('email','=',get_email),('b2c_customer','!=',False)] , limit=1).email


class Inheirt_surveeys(models.Model):
	_inherit = 'survey.survey'
	company_id_custom = fields.Many2one('res.company',string="Company" , default=lambda self: self.env['res.company'].search([]), readonly=True , store=True)
	default_mail_id_custom = fields.Many2one('ir.mail_server',string="Mail Server" , default=lambda self: self.env['ir.mail_server'].search([]), readonly=True , store=True)

	def send_survey_emails_to_contacts(self,x,y):
		email_from = self.env['ir.mail_server'].sudo().search([],limit=1)
		mail_obj = self.env['mail.mail']
		send_to = "{0}".format(y.email)
		survey_name = x.title

		form_design = """

			<div style="margin: 0px; padding: 0px; font-size: 13px;">
					<p style="margin: 0px; padding: 0px; font-size: 13px;">
						<b>
						Dear {{y.name}}!</b><br /><br />
						Thank you for choosing Togather Tourism, <br />

						We craft Unlimited luxury for Mind, Body and Soul.   <br />  

						We would appreciate it if you would take a moment to provide your feedback on your recent trip with us. <br />
						<br />

						<div style="margin: 16px 0px 16px 0px;">
							<a href="{{x.public_url}}" style="color:#fff !important; background-color: #DAD7DD; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">
								Start Survey
							</a>
						</div>
						<br />



						We always endeavor to exceed every guest’s expectations and your feedback is a valuable contribution in improving our service.    <br />

						We greatly look forward to your return and value your patronage. <br />

						
						
					   Please don't hesitate to contact your Travel Consultant  anytime!
					   <br />
					   <br />

					   <b> Thank you! </b>
						<br />

					 
					</p>
				</div>

		"""
		
		template = Environment(loader=BaseLoader).from_string(form_design)
		template_vars = {

		'x':x,
		'y':y

		}
		html_out = template.render(template_vars)
		my_mail =  mail_obj.sudo().create({
		'email_from': email_from.smtp_user,
		'email_to': send_to,
		'model': 'survey.survey',
        'res_id':self.id,
		'subject': "Participate to " + str(survey_name),
		'body_html':
		'''<span  style="font-size: 14px"><br/>
		  <br/>%s </span> 
		  <br/><br/>''' % (html_out)}).sudo().send()



	def send_email_to_clients_for_surevy(self):

		surveys = self.env['survey.survey'].sudo().search([] , limit=1)
		
		surveys_users = self.env['survey.user_input'].sudo().search([])
		
		all_contacts = self.env['res.partner'].sudo().search([('b2c_customer','!=',False),('email','!=',False)])

		all_partners_data = []

		for alls in surveys_users:

			all_partners_data.append(alls.partner_id.id)
		for x in surveys:
			for y in all_contacts:

				all_related_res = self.env['reservation.order'].sudo().search([('partner_id','=',y.id),('email_count','!=',3)])
				for z in all_related_res:
					for c in z.flights_pkg:

						current_date_get = datetime.now()
						if c.arrival:
							if current_date_get >= c.arrival:

								if y.id not in all_partners_data:

									if y.email:
										z.email_count +=1

										# print(y.id)
										x.send_survey_emails_to_contacts(surveys,y)
										# print(y.id)
										break
								else:
									pass

class SurveyInvite_inheritt(models.TransientModel):
	_inherit = 'survey.invite'
	survey_id = fields.Many2one('survey.survey', string='Survey', required=True)

	@api.model
	def _get_default_from(self):
		if self.env.user.email:
			return 'reservations@rawnaqtourism.com'
		raise UserError(_("Unable to post message, please configure the sender's email address."))
	email_from = fields.Char('From', default=_get_default_from, help="Email address of the sender.")
