# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartnerSequence(models.Model):
	_inherit = 'res.partner'
	# _description = 'Adding sequence for vendors and customers'
	_order = 'id'


	def sync_partners_to_mailing_list(self):
		"""Sync res.partner customers to Mailing List Contacts"""
		mailing_contact_model = self.env['mailing.contact']
		mailing_list_model = self.env['mailing.list']

		# **Step 1: Ensure Mailing List Exists**
		mailing_list = mailing_list_model.search([('name', '=', 'Customers')], limit=1)
		if not mailing_list:
			mailing_list = mailing_list_model.create({'name': 'Customers'})

		# **Step 2: Get Existing Name + Email in Mailing List**
		existing_contacts = mailing_contact_model.search([('list_ids', 'in', mailing_list.id)])
		
		# **Map Names & Emails Together to Prevent Duplicates**
		existing_contact_map = {(contact.name, contact.email) for contact in existing_contacts}

		# **Step 3: Get Customers from res.partner**
		partners = self.env['res.partner'].search([('email', '!=', False), ('partner_type', '=', 'customer')])

		contacts_to_create = []
		for partner in partners:
			# Check both (name, email) combination
			if (partner.name, partner.email) not in existing_contact_map:
				contacts_to_create.append({
					'name': partner.name,
					'email': partner.email,
					'list_ids': [(6, 0, [mailing_list.id])],  # **Assign Mailing List**
				})

		# **Step 4: Create New Contacts in Mailing List**
		if contacts_to_create:
			mailing_contact_model.create(contacts_to_create)

		return True


	reservation_count = fields.Integer(
		compute="_compute_reservation_count"
	)

	def _compute_reservation_count(self):
		for partner in self:
			partner.reservation_count = self.env['reservation.order'].search_count([('partner_id', '=', partner.id)])

	def action_open_partner_orders(self):
		return {
			'type': 'ir.actions.act_window',
			'name': 'Reservations',
			'res_model': 'reservation.order',
			'view_mode': 'list,form',
			'domain': [('partner_id', '=', self.id)],
			'context': {'default_partner_id': self.id},
			'views': [(self.env.ref('travel_package.reservation_order_tree_ext').id, 'list'), (self.env.ref('travel_package.view_reservation_order_form').id, 'form')],
		}

	def _get_current_user(self):
		is_admin_user = bool(self.env.user.admin_user)
		current_partner_id = self.env.user.partner_id.id
		for partner in self:
			partner.current_user = partner.id == current_partner_id or is_admin_user
	


			
	# current_user = fields.Many2one('res.partner','Current User', compute='_get_current_user')
	current_user = fields.Boolean('Current User', compute='_get_current_user')
	serial_no = fields.Char('Serial No',tracking=True)
	partner_type = fields.Selection([
	('customer', 'Customer'),
	('supplier', 'Supplier'),
	('others', 'Others'),
	], string="Partner Type",tracking=True)

	company_registration = fields.Char(string="Company Registration Number",tracking=True)

	financial_term = fields.Selection([
	('pre_paid', 'Pre-Paid'),
	('credit', 'Credit'),
	], string="Financial Term",default='pre_paid')
	has_moves = fields.Boolean(store=False)

	credit_days = fields.Char('Credit Duration(Days)',tracking=True)
	name = fields.Char(index=True,tracking=True)
	phone = fields.Char(tracking=True)
	total_all_due = fields.Float(tracking=True)



	@api.model_create_multi
	def create(self, vals_list):
		partner_search_mode = self.env.context.get('res_partner_search_mode')
		for vals in vals_list:
			partner_type = vals.get('partner_type') or partner_search_mode
			if not vals.get('serial_no') and partner_type == 'customer':
				vals['serial_no'] = self.env['ir.sequence'].next_by_code('cr.sequence')
			elif not vals.get('serial_no') and partner_type == 'supplier':
				vals['serial_no'] = self.env['ir.sequence'].next_by_code('vr.sequence')
		return super(ResPartnerSequence, self).create(vals_list)

class res_seeting(models.Model):
	_inherit = 'res.users'

	admin_user = fields.Boolean('Accounting Admin/All Records',help="This checkbox funcitionalty for accounting module. \n If it is true then all invocies, bills,vendor or customer credit note, payments and JE or all users will show. \n Othewr wise user will check only own documents of accounting.")
