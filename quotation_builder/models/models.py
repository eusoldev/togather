# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from datetime import date
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import datetime as dt

from bs4 import BeautifulSoup

import json

import odoo.exceptions

import datetime as dt
import ast


import requests

from odoo import http

from odoo.http import request

import http.client

from lxml import etree
import uuid


class quotation_builder(models.Model):
	_name = 'quotation.builder'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = 'Quotation Builder'
	_rec_name ='sr_no'
	_order = "id desc"


	subject = fields.Char(string="Subject" , tracking=True)
	cancellation_days = fields.Integer(string="Cancellation day")
	destination = fields.Many2many('destination.name', string="Destination")
	client_name = fields.Many2one('res.partner',string="Client Name", tracking=True)
	creation_date = fields.Datetime(string="Creation Date", default=lambda self: fields.datetime.now()+ timedelta(hours=5))
	reference = fields.Char(string="Ref Number", tracking=True) 
	maldives_website_link = fields.Boolean(string="Maldives Website Link") 
	total_in_report = fields.Boolean(string="Show Total in Report") 
	sr_no = fields.Char() 
	state = fields.Selection([
		('draft', 'Draft'),
		('validate', 'Validate'),
		# ('approved', 'Approved')
	], string='State', default='draft', tracking=True)
	partner_id_mtom = fields.Many2many('res.partner', string ="Family List", tracking=True)
	tree_link_id = fields.One2many('quotation.builder.tree', 'tree_link')
	flights_pkg = fields.One2many('quotation.builder.tree','flights_return', tracking=True)
	transportation_pkg = fields.One2many('quotation.builder.tree','transportation_return', tracking=True)
	tours_pkg = fields.One2many('quotation.builder.tree','tours_return', tracking=True)
	visa_pkg = fields.One2many('quotation.builder.tree','visa_return', tracking=True)
	packages_pkg = fields.One2many('quotation.builder.tree','package_return', tracking=True)
	privatejet_pkg = fields.One2many('quotation.builder.tree','privatejet_return', tracking=True)
	yacht_pkg = fields.One2many('quotation.builder.tree','yacht_return', tracking=True)
	cruises_pkg = fields.One2many('quotation.builder.tree','cruises_return', tracking=True)
	otherservices_pkg = fields.One2many('quotation.builder.tree','otherservices_return', tracking=True)
	date_to = fields.Datetime(string="Date To")
	date_from = fields.Datetime(string="Date From",required=True)
	company_id = fields.Many2one('res.company', string='Company', default= lambda self: self.env.company)
	destination_pictures = fields.Many2many(
		'ir.attachment',
		string='Destination pictures',
		help='Attach pictures to this record.',
	)

	number_of_guests = fields.Integer(string="Guests")
	no_of_nights= fields.Integer(string="No of nights")

	offers_validity_date = fields.Date('Offers Validity Date')
	# @api.onchange('creation_date', 'date_to')
	# def get_the_number_of_nights(self):
	# 	for rec in self:
	# 		if rec.creation_date and rec.date_to:
	# 			creation_date = fields.Datetime.from_string(rec.creation_date + timedelta(hours=5))
	# 			date_to = fields.Datetime.from_string(rec.date_to + timedelta(hours=5))

	# 			delta_days = (date_to.date() - creation_date.date()).days

	# 			rec.no_of_nights=delta_days - 1 if creation_date.date() != date_to.date() else rec.no_of_nights == delta_days

	# 			rec.no_of_days = delta_days+1
	# 			rec.no_of_nights=rec.no_of_nights+1

	@api.onchange('creation_date', 'date_to')
	def onchange_dates(self):
		if self.creation_date and self.date_to and self.creation_date > self.date_to:
			raise ValidationError('Date From is greater than Date To')

	def write(self, vals):
		for x in self:
			if 'date_to' in vals:
				date_to = vals.get('date_to')
				date_to = datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S")
			else:
				date_to =  x.date_to
			if 'creation_date' in vals:
				creation_date = vals.get('creation_date')
				creation_date = datetime.strptime(creation_date, "%Y-%m-%d %H:%M:%S")
			else:
				creation_date =  x.creation_date
			if creation_date and date_to:
				if creation_date > date_to: 
					raise  ValidationError('Date From is greater than Date To')
		new_record = super(quotation_builder, self).write(vals)
		return new_record





	def action_hotel_email_history(self):
		return {
			'type': 'ir.actions.act_window',
			'name': 'History',
			'res_model': 'mail.message',
			'view_type': 'form',
			'view_mode': 'list,form',
			'domain': [('res_id', '=',self.id),('model', '=','quotation.builder')],
			}

	def _get_default_note_eng(self):
		result = """
		<p>days before arrival,after that you could amend your booking dates depending on availabilty and price subject to change.</p>
										<p>- All the above rates and availabilty are price subject to Change.</p>
										"""


		return result





	def _get_default_note_ar(self):
		result = """
			<p>
			‫یوم‬ ‫فقط‬, ‫بعد‬ ‫ذلك‬ ‫یمكن‬ ‫تعدیل‬ ‫التاریخ‬ ‫فقط‬ ‫وفقا‬ ‫لأمكانیة‬ ‫الحجز‬ ‫والسعر‬ ‫المتاح‬ ‬
		</p>
		<p>
			‫- ‫جمیع‬ ‫الامكانیات‬ ‫والاسعار‬ ‫قابلة‬ ‫للتغییر
		</p>
		 """


		return result


	cancel_new_eng = fields.Text('General Cancellation Policy (English)' , default=_get_default_note_eng)
	cancel_new_ar = fields.Text('General Cancellation Policy (Arabic)'  ,    default=_get_default_note_ar) 


	terms_conditions_eng = fields.Text('Terms & Conditions (English)') 
	terms_conditions_ar = fields.Text('Terms & Conditions (Arabic)') 

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
		if self.client_name.email:
			reservation_ref = self.sr_no
			in_email = self.client_name.email
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




	def button_draft(self):
		self.state='draft'

	def button_validate(self):
		self.state='validate'

	def unlink(self): 
		for x in self: 
			if x.state == 'validate': 
				raise ValidationError('Cannot Delete Record') 
		rec = super(quotation_builder,self).unlink()
		return rec





	def google_maps_getting(self,req):

		ret = requests.get(req).text
		soup = BeautifulSoup(ret, features ='html.parser')
		img_listings = soup.find_all("img",class_="mimg vimgld") 
		img_url = 'https://i.ibb.co/6FZdJ6f/Maldives-featured.jpg'
		
		if img_listings:
			img_url = img_listings[0]['data-src']
			return img_url

		else:
			return img_url

	def button_send_email_now(self):
		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		try:
			template_id = ir_model_data._xmlid_lookup('quotation_builder.quotation_email_pro_clients')[1]
		except ValueError:
			template_id = False

		try:
			compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form_id = False

		can_date = self.creation_date+ relativedelta(days=self.cancellation_days , hours=6)
		rooms_get_result = ''
		meals_get_result = ''
		transs_get_result = ''
		for link in self.tree_link_id:
			if link.room_type:
				rooms_get = ''
				for room in link.room_type:
					rooms_get += room.name + ', ' 
				result = ', '.join([s for s in rooms_get.split(', ') if s])
				rooms_get_result = result

			if link.meal_plane:
				meals_get=''
				for meal in link.meal_plane:
					meals_get += meal.name + ', ' 
				result = ', '.join([s for s in meals_get.split(', ') if s])
				meals_get_result = result
			if link.transfer:
				transs_get = ''
				for trans in link.transfer:
					transs_get += trans.name + ', ' 
				result = ', '.join([s for s in transs_get.split(', ') if s])
				transs_get_result = result

		if self.tree_link_id:
			for get in self.tree_link_id:
				if get.resort_name:

					for x in get.resort_name:
					
						url = "https://www.bing.com/images/search?q="

						if x.company_type == 'company':
							if x.name:
								url += x.name.replace(' ','+')
							if x.street_name:
								url += x.street_name.replace(' ','+')
							if x.street2:
								url += x.street2.replace(' ','+')
							if x.street_number:
								url += x.street_number.replace(' ','+')
							if x.street_number2:
								url += x.street_number2.replace(' ','+')
							if x.city:
								url += '+'+x.city.replace(' ','+')
							if x.state_id:
								url += '+'+x.state_id.name.replace(' ','+')
							get_image_url = self.google_maps_getting(url)
							get.image_url = get_image_url

						else:
							if x.name:
								url += x.name.replace(' ','+')
							if x.ind_street:
								url += x.ind_street.replace(' ','+')
							if x.ind_street2:
								url += x.ind_street2.replace(' ','+')
							if x.ind_city:
								url += '+'+x.ind_city.replace(' ','+')
							if x.ind_state_id:
								url += '+'+x.ind_state_id.name.replace(' ','+')

							get_image_url = self.google_maps_getting(url)
							get.image_url = get_image_url

				else:
					pass
					
		ctx = {
			'villas': rooms_get_result,
			'meals': meals_get_result,
			'transfers': transs_get_result,
			'default_model': 'quotation.builder',
			'default_res_ids': self.ids,
			'default_use_template': bool(template_id),
			'default_template_id': template_id,
			'default_composition_mode': 'comment',
		}
		return {
			'name': _('Quotation Email'),
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(compose_form_id, 'form')],
			'view_id': compose_form_id,
			'target': 'new',
			'context': ctx,
		}



	# @api.model
	# def create(self, vals):
	#     if vals['client_name']:
	#         vals['sr_no'] = self.env['ir.sequence'].next_by_code('quotation.seq')
	#     new_record = super(quotation_builder, self).create(vals)

	#     return new_record

	@api.onchange('client_name')
	def get_guest_info(self):
		if self.client_name:
			liste = []
			if self.client_name.sub_customer:
				liste.append(self.client_name.id)
				for x in self.client_name.sub_customer:
					liste.append(x.customer_name.id)
				if liste:
					self.partner_id_mtom = [(6,0,liste)]
			else:
				self.partner_id_mtom = self.client_name.ids




class quotation_builder_tree(models.Model):
	_name = 'quotation.builder.tree'
	_rec_name = 'resort_name'
	_description = 'Quotation Builder Tree'



	def ext_search_product(self):
		search = self.env['product.product'].sudo().search([('prod_serv_typecategory','=','hotel')], limit=1)
		if search:
			return search.id
		else:
			return 0
	resort_name = fields.Many2one('res.partner',string="Hotel Name")
	resort_map = fields.Char(string="Hotel Map")
	# , compute="_get_resort_map"
	offers_appiled = fields.Text(string="Note") 
	tree_canelattions = fields.Text(string="Cancellation") 
	product_id = fields.Many2one('product.product',"Services", default=ext_search_product)

	check_in = fields.Date(string="Check In")
	image_url = fields.Char(string="Image Url For Emails")
	check_out = fields.Date(string="Check Out")
	no_of_nights = fields.Integer(string="Number of Nights")
	passenger = fields.Many2many('res.partner',string="Passenger")
	number_of_rooms = fields.Integer(string=" Number of Rooms")
	room_type = fields.Many2many('room.type',string="Room Type")
	transfer = fields.Many2many('hotel.transfer',string="Transfer")
	total = fields.Float(string="Total")
	no_of_guest = fields.Char(string="No of Guests")
	meal_plane = fields.Many2many('meal.plan',string="Meal Plan")
	inclusion = fields.Many2one('quotation.builder.inclusion',string="Inclusions")
	tree_link = fields.Many2one('quotation.builder')
	drag=fields.Integer(string="Drag",default="10")
	date_of_birth = fields.Date(string="Date Of Birth", store=True)
	total_age_calculate = fields.Char(string="Age",store=True, compute='_comute_age')
	cancellation_days = fields.Date(string="Cancellation Day")
	city_id = fields.Many2one('city.codes', string="City")
	pictures = fields.Many2many(
		'ir.attachment',
		string='Pictures',
		help='Attach pictures to this record.',
	)


	@api.depends('date_of_birth','category')
	def _comute_age(self):
		for r in self:
			if r.date_of_birth:
				today = date.today()
				age_delta = relativedelta(today, r.date_of_birth)
				years = age_delta.years
				months = age_delta.months

				# Age string
				r.total_age_calculate = f"{years} Years {months} Months"

				# Category based on age
				total_months = (years * 12) + months
				if total_months <= 36:
					r.category = 'infant'
				elif 36 <= total_months <= 132:
					r.category = 'child'
				elif total_months >= 144:
					r.category = 'adult'
				else:
					r.category = False  # For ages between 25–35 months or 133–143 months if needed
			else:
				r.total_age_calculate = False
				r.category = False


	gender = fields.Selection([
		('male', 'Male'),
		('female', 'Female'),
	], string='Gender', default='male')

	category = fields.Selection([
		('infant', 'Infant'),
		('child', 'Child'),
		('adult', 'Adult')
	], string='Category', default='adult', compute='_compute_age', store=True)
	supplier = fields.Many2one('res.partner',"Supplier")
	customer = fields.Many2one('res.partner',"C Name")
	partner_id_mtom_parent = fields.Many2many('res.partner','ppp_idd','ppp_keyy',string="Parents Customer Name")
	customer_m2m = fields.Many2many('res.partner','ppppp_idd','ppppp_keyy',string="Customer")
	from_to = fields.Char("From/To")
	flight = fields.Char(string='Flight')
	fight_class = fields.Many2one('fight.class',string='Class')
	e_ticket = fields.Char(string='E-Ticket')
	e_ticket_m2m = fields.Many2many('electronic.ticket',string='E-Ticket')
	bag = fields.Char(string='Bag')
	occasion = fields.Char(string='Occasion')
	special_remarks = fields.Char(string='Special Remarks')
	


	# flights_fileds
	airline = fields.Many2one('res.partner',"Airline",domain="[('airline_supplier','=',True)]")
	from_loc = fields.Many2one('city.codes', "From")
	to_loc = fields.Many2one('city.codes', "To")
	departures = fields.Datetime("Departures Date")
	arrival = fields.Datetime("Return Date")
	booking_date = fields.Date(string="Booking Date",required =True, default=lambda self: fields.Date.today())
	description = fields.Text("Description")
	airline_pnr = fields.Char(string='Airline PNR')
	pick_up_place = fields.Char("Pick Up")
	drop_of_place = fields.Char("Drop-off")
	date = fields.Datetime("Date" ,default=datetime.now().replace(hour=19, minute=0, second=0))
	transfer_type = fields.Many2one('transfer.type', string="Transfer Type")
	# cruises fields
	confirmation_no = fields.Char("Confirmation Number")
	duration = fields.Float(string="Duration")
	cabin_type = fields.Many2one("cabin.type", string='Cabin Type')
	departure_place = fields.Char(string="Departure Place")
	occupancy = fields.Char(string="Occupancy")
	arrival_place = fields.Char(string="Arrival Place")
	date_from =fields.Date("Date from")
	date_to =fields.Date("Date to")
	vehicle_type = fields.Many2one('vehicle.type', string="Vehicle Type")
	wait_time_policy = fields.Many2one('wait.time.policy', string="Waiting Time Policy")
	rent_car = fields.Char("Rent Car")
	added_values = fields.Char("Added Values")
	product_type = fields.Char("Product Type")
	terminal = fields.Char(string='Terminal')
	yacht_type = fields.Many2one("yacht.type", string='Yacht Type')
	no_of_person = fields.Float("No. of Guests ",default=1)
	currency_name= fields.Many2one('res.currency', "Currency")
	price = fields.Float("Net Amount")
	commission_percentage= fields.Float("Commission%")
	commission= fields.Float("Commission")
	days_valid = fields.Many2one('days.name',"Days Valid")
	ticket_day = fields.Date("Ticket Day")
	visa_status = fields.Selection([('draft', 'Requested Documents'),
	('recieved', 'Recieved Documents'),
	('incomplete', 'Incomplete Documents')],string='Visa Status')
	rooms_type = fields.Char("Room Type")
	meal_plan= fields.Many2one('meal.plan', string="Meal Plan")

	# package_fields
	validity = fields.Char("Validity (Start/Expire)")
	transfer_mode = fields.Char("Transfer Mode")

	# tour
	guided_or_not = fields.Selection([('guided', 'Guided'),
	('not_guided', 'Not Guided'),
	],string='Guided/Not Guided')




	service_type = fields.Selection([
		('flight', 'Flight'),
		('hotel', 'Hotel'),
		('transfer', 'Transfer'),
		('tour', 'Tour'),
		('visa', 'Visa'),
		('package', 'Package'),
		('private', 'Private Jet'),
		('yacht', 'Yacht'),
		('cruise', 'Cruise'),
		('other', 'Other Service'),
		],string='Service Type',related="product_id.prod_serv_typecategory")

	# @api.onchange('supplier','customer_m2m')
	# def get_default_product(self):

	# 	if self.service_type != False:
	# 		search = ('id','!=',False)
	# 		if self.service_type == 'flight':
	# 			search = ('prod_serv_typecategory', '=','flight')
	# 		if self.service_type == 'hotel':
	# 			search = ('prod_serv_typecategory', '=','hotel')
	# 		if self.service_type == 'transfer':
	# 			search = ('prod_serv_typecategory', '=','transfer')
	# 		if self.service_type == 'tours':
	# 			search = ('prod_serv_typecategory', '=','tour')
	# 		if self.service_type == 'visa':
	# 			search = ('prod_serv_typecategory', '=','visa')
	# 		if self.service_type == 'ready_package':
	# 			search = ('prod_serv_typecategory', '=','package')
	# 		if self.service_type == 'private_jet':
	# 			search = ('prod_serv_typecategory', '=','private')
	# 		if self.service_type == 'yacht':
	# 			search = ('prod_serv_typecategory', '=','yacht')
	# 		if self.service_type == 'cruise':
	# 			search = ('prod_serv_typecategory', '=','cruise')
	# 		if self.service_type == 'other':
	# 			search = ('prod_serv_typecategory', '=','other')
	# 		record = self.env['product.product'].search([search],limit=1)
	# 		self.product_id = record.id

	services_return = fields.Many2one('quotation.builder')
	flights_return = fields.Many2one('quotation.builder')
	package_return = fields.Many2one('quotation.builder')
	yacht_return = fields.Many2one('quotation.builder')
	cruises_return = fields.Many2one('quotation.builder')
	privatejet_return = fields.Many2one('quotation.builder')
	otherservices_return = fields.Many2one('quotation.builder')
	tours_return = fields.Many2one('quotation.builder')
	itinarnay_return = fields.Many2one('quotation.builder')
	transportation_return = fields.Many2one('quotation.builder')
	visa_return = fields.Many2one('quotation.builder')


	# @api.onchange('booking_date', 'departures', 'check_in', 'ticket_day', 'date_from')
	# def onchange_dates_validation(self):

	# 	if self.service_type and self.booking_date:
	# 		previous_record = self.env['quotation.builder.tree'].search([
	# 			('booking_date', '=', self.booking_date),
	# 			('departures', '=', self.departures),
	# 			('check_in', '=', self.check_in),
	# 			('ticket_day', '=', self.ticket_day),
	# 			('date_from', '=', self.date_from),
	# 		], order='booking_date desc', limit=1)

	# 		print(previous_record)

	# 		if previous_record:
	# 			if self.service_type == 'flight' and self.departures <= previous_record.departures:
	# 				raise ValidationError("Departure date must be greater than previous record date.")
	# 			elif self.service_type == 'hotel' and self.check_in <= previous_record.check_in:
	# 				raise ValidationError("Check-in date must be greater than previous record date.")
	# 			elif self.service_type == 'tour' and self.ticket_day <= previous_record.ticket_day:
	# 				raise ValidationError("Ticket date must be greater than previous record date.")
	# 			elif self.service_type == 'other' and self.date_from <= previous_record.date_from:
	# 				raise ValidationError("Date from must be greater than previous record date.")



	rate_hotel = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.ref('base.SAR'))
	total_selection = fields.Selection([('same','Same'),('different','Different')],default='different',string="Total Selection",compute="get_total_selection")

	customer_city = fields.Char(string="Customer City", compute='_compute_customer_info', store=True)
	destination_country = fields.Char(string="Destination Country", compute='_compute_customer_info', store=True)

	

	@api.depends('resort_name')
	def _compute_customer_info(self):
		for line in self:
			partner = line.resort_name
			line.customer_city = partner.city or ''
			line.destination_country = partner.country_id.name or ''

	def get_total_selection(self):
		for tree in self:
			tree.total_selection = 'different'
			if tree.tree_link:
				tree_privious = tree.search([('tree_link','=',tree.tree_link.id),('id','!=',tree.id)])
				if tree_privious:
					for privious in tree_privious:
						# tree_privious = tree_privious[-1]
						if tree.check_in == privious.check_in and tree.check_out == privious.check_out:
							tree.total_selection = 'same'

	@api.onchange('resort_map' , 'resort_name')
	def _get_resort_map(self):


		url = ''
		if self.resort_name:

			for y in self:
				for x in y.resort_name:
					
					url = "http://maps.google.com/maps?oi=map&q="

					if x.company_type == 'company':
						if x.name:
							url += x.name.replace(' ','+')
						if x.street:
							url += x.street.replace(' ','+')
						if x.street2:
							url += x.street2.replace(' ','+')
						# if x.street_number:
						# 	url += x.street_number.replace(' ','+')
						# if x.street_number2:
						# 	url += x.street_number2.replace(' ','+')
						if x.city:
							url += '+'+x.city.replace(' ','+')
						if x.state_id:
							url += '+'+x.state_id.name.replace(' ','+')
						if x.zip:
							url += '+'+x.zip.replace(' ','+')
						if x.country_id:
							url += '+'+x.country_id.name.replace(' ','+')
						y.resort_map = url

					else:
						if x.name:
							url += x.name.replace(' ','+')
						if x.ind_street:
							url += x.ind_street.replace(' ','+')
						if x.ind_street2:
							url += x.ind_street2.replace(' ','+')
						if x.ind_city:
							url += '+'+x.ind_city.replace(' ','+')
						if x.ind_state_id:
							url += '+'+x.ind_state_id.name.replace(' ','+')
						if x.ind_zip:
							url += '+'+x.ind_zip.replace(' ','+')
						if x.ind_country_id:
							url += '+'+x.ind_country_id.name.replace(' ','+')

						y.resort_map = url



		else:
			self.resort_map = "No Map Available"


	@api.onchange('check_in','check_out')
	def date_error(self):
		for x in self:
			if x.check_out and x.check_in:
				if x.check_out < x.check_in: 
					raise  ValidationError('Check In is greater than Check Out.')


	@api.onchange('check_in','check_out')
	def get_the_number_of_nights(self):
		if self.check_out and self.check_in:
			delta = self.check_out - self.check_in
			self.no_of_nights = delta.days
		else:
			self.no_of_nights = 0


class quotation_builder_inclusion(models.Model):
	_name = 'quotation.builder.inclusion'
	_rec_name = 'name'
	_description = 'Quotation Builder Inclusions'

	name = fields.Char(string="Name")
	inclusion = fields.Html(string="Inclusions")



