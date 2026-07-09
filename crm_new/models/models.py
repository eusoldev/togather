# -*- coding: utf-8 -*-

from odoo import models, fields, api

class crm_new(models.Model):
	_name = 'crm.new'
	_description = "Travel Type"
	_rec_name = 'travel_type'

	travel_type = fields.Char(string="Travel Type", required=True)

class quotation_builder_inherit(models.Model):
	_inherit = 'quotation.builder'

	lead_id = fields.Many2one('crm.lead', string="Lead", copy=False)

	def action_view_crm_lead(self):
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'name': 'CRM Lead',
			'res_model': 'crm.lead',
			'view_mode': 'form',
			'res_id': self.lead_id.id,
			'target': 'current',
		}

class sale_order_inherit(models.Model):
	_inherit = 'reservation.order'

	lead_id = fields.Many2one('crm.lead', string="Lead", copy=False)

	def action_view_crm_lead(self):
		self.ensure_one()
		lead_id = self.lead_id
		return {
		'type': 'ir.actions.act_window',
		'name': 'CRM Lead',
		'res_model': 'crm.lead',
		'view_mode': 'form',
		'res_id': lead_id.id,
		'target': 'current',
	}

class crm_inherit(models.Model):
	_inherit = 'crm.lead'

	travel_type = fields.Many2one('crm.new', string="Travel Type")
	enquiry_type = fields.Selection([
		('b2b', 'B2B'),
		('ta', 'Travel Agents (B2B)'),
	], string='Enquiry Type', default='b2b')

	guest1 = fields.Integer(string="Adults")
	guest2 = fields.Integer(string="Kids")
	guest3 = fields.Integer(string="Infants")
	total_guest = fields.Float(string="Total Guests", compute="get_total_guests")

	trip_date_from = fields.Date(string="Trip Start Date")
	trip_date_to = fields.Date(string="Trip End Date")

	quotation_builder_count = fields.Integer(compute='_compute_quotation_builder_count')
	reservation_count = fields.Integer(compute='_compute_reservation_count')

	@api.depends('guest1', 'guest2', 'guest3')
	def get_total_guests(self):
		for rec in self:
			rec.total_guest = rec.guest1 + rec.guest2 + rec.guest3

	def _compute_quotation_builder_count(self):
		for rec in self:
			rec.quotation_builder_count = self.env['quotation.builder'].search_count([('lead_id', '=', rec.id)])

	def _compute_reservation_count(self):
		for rec in self:
			rec.reservation_count = self.env['reservation.order'].search_count([('lead_id', '=', rec.id), ('package', '=', True)])

	def action_create_quotation_builder(self):
		self.ensure_one()
		vals = {
			'client_name': self.partner_id.id,
			'subject': self.name,
			'sr_no': self.name,
			'number_of_guests': int(self.total_guest),
			'lead_id': self.id,
			'date_from': self.trip_date_from,
			'date_to': self.trip_date_to,
		}
		quotation = self.env['quotation.builder'].create(vals)
		return {
			'type': 'ir.actions.act_window',
			'name': 'Quotation Builder',
			'res_model': 'quotation.builder',
			'view_mode': 'form',
			'res_id': quotation.id,
			'target': 'current',
		}

	def action_create_reservation(self):
		self.ensure_one()
		vals = {
			'partner_id': self.partner_id.id,
			'name_package': self.name,
			'no_of_particpents': int(self.total_guest),
			'lead_id': self.id,
			'package': True,
			'opportunity_id': self.id,
			'arrival_date': self.trip_date_from,
			'departure_date': self.trip_date_to,
		}
		reservation = self.env['reservation.order'].create(vals)
		return {
			'type': 'ir.actions.act_window',
			'name': 'Reservation',
			'res_model': 'reservation.order',
			'view_mode': 'form',
			'res_id': reservation.id,
			'view_id': self.env.ref('travel_package.view_reservation_order_form').id,
			'target': 'current',
		}

	def action_view_quotation_builders(self):
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'name': 'Quotation Builders',
			'res_model': 'quotation.builder',
			'view_mode': 'list,form',
			'domain': [('lead_id', '=', self.id)],
			'context': {'default_lead_id': self.id},
		}

	def action_view_reservations(self):
		self.ensure_one()
		view_id = self.env.ref('travel_package.view_reservation_order_form').id
		return {
			'type': 'ir.actions.act_window',
			'name': 'Reservations',
			'res_model': 'reservation.order',
			'view_mode': 'list,form',
			'views': [(False, 'list'), (view_id, 'form')],
			'domain': [('lead_id', '=', self.id), ('package', '=', True)],
			'context': {'default_lead_id': self.id, 'default_package': True},
		}

	last_builder_ref = fields.Char(compute='_compute_trip_refs', string="Builder Ref")
	last_reservation_ref = fields.Char(compute='_compute_trip_refs', string="Reservation Ref")

	def _compute_trip_refs(self):
		for rec in self:
			builder = self.env['quotation.builder'].search([('lead_id', '=', rec.id)], order='id desc', limit=1)
			rec.last_builder_ref = builder.sr_no if builder else False
			
			res = self.env['reservation.order'].search([('lead_id', '=', rec.id), ('package', '=', True)], order='id desc', limit=1)
			rec.last_reservation_ref = res.name if res else False

	# @api.depends('order_ids.state', 'order_ids.currency_id', 'order_ids.amount_total', 'order_ids.package_total', 'order_ids.package')
	# def _compute_sale_data(self):
	# 	# Override sale_crm standard calculation to use package_total
	# 	super()._compute_sale_data()
	# 	for lead in self:
	# 		total = 0.0
	# 		# Include all package orders (even draft ones) so user doesn't see 0
	# 		quotations = lead.order_ids.filtered(lambda l: l.package)
	# 		for order in quotations:
	# 			total += order.package_total
	# 		lead.sale_amount_total = total

class CRM_Access_Rights_c(models.Model):
	_inherit = 'res.users'

	def get_related_crm_records_now(self):
		user = self.env.user
		if user.has_group('crm_new.group_crm_admin'):
			return self.env['crm.lead'].with_context(active_test=False).search([]).ids
		if user.has_group('crm_new.group_crm_user_ext'):
			if user.id in [9, 11]:
				return self.env['crm.lead'].with_context(active_test=False).search([]).ids
			return self.env['crm.lead'].with_context(active_test=False).search([('user_id', '=', user.id)]).ids
		return []
