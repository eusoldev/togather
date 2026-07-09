# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError, UserError





class SOCancelationExt(models.Model):
	_inherit = 'reservation.order'
	# _description = "Travel Package Cancelation"

	def action_cancel(self):
		return {
				'res_model': 'package.cancelation.wizard',
				'type': 'ir.actions.act_window',
				'view_mode': 'form',
				'name':'Package Cancelation',
				'view_type': 'form',
				'target': 'new',
				# 'domain': [('invoice_origin','like',self.name)],
				 'context': dict(
					 default_package_id=self.id,
				),
				}
				

	# flight_cancelation_charges = fields.Float('Flight Cancelation Charges')
	cancel_tree = fields.One2many('cancel.charge', 'cancel_rel', string='Flight')
	

class CancelationCharges(models.Model):
	_name = 'cancel.charge'
	_description = "Travel Package Cancelation"

	@api.model
	def create(self, vals):
		cancel_rec = self.env['cancel.charge'].search([('partner_id','=',vals['partner_id']),('cancel_rel','=',vals['cancel_rel']),('service_type','=',vals['service_type'])])
		if cancel_rec:
			raise ValidationError("Can't create more than one Cancelation against single vendor with same service type")
		new_rec = super(CancelationCharges, self).create(vals)

		return new_rec

	partner_id = fields.Many2one('res.partner', "Vendor")
	charges = fields.Float("Charges")
	service_type = fields.Selection([
		('flight', 'Flight'),
		('hotel', 'Hotel'),
		('transfer', 'Transfer'),
		('tours', 'Tours'),
		('visa', 'Visa'),
		('ready_package', 'Ready Package'),
		('private_jet', 'Private Jet'),
		('yacht', 'Yacht'),
		('cruise', 'Cruise'),
		('other', 'Other'),
		],string='Service Type')


	cancel_rel = fields.Many2one("reservation.order")
	
class PackageCancelation(models.TransientModel):
	_name = "package.cancelation.wizard"
	_description = "Wizard model for package cancelation"

	reason_to_cancel = fields.Char("Reason To Cancel")
	cancelation_charges = fields.Float("Cancelation Charges")
	# include_vendor_charges = fields.Boolean("Include Vendor Charges")
	create_customer_refund = fields.Boolean("Create Customer Refund")
	create_vendor_refund = fields.Boolean("Create Vendor Refund")
	package_id = fields.Many2one('reservation.order', 'Package')
	
	# def cancel_package(self):



	def cancel_package(self):

		# canceling previous invoices and bills
		cust_invs = self.env['account.move'].search([('invoice_origin','like',self.package_id.name),('move_type','=','out_invoice')])
		vendor_bills = self.env['account.move'].search([('invoice_origin','like',self.package_id.name),('move_type','=','in_invoice')])

		self.package_id.write({
			'stages':'cancel',
			'reason_to_cancel':self.reason_to_cancel,
			})

		invoices = self.env['account.move'].search([('state','=','posted'),('package_no','=',self.package_id.name),('move_type','=','in_invoice')])

		existing_invoice = self.env['account.move'].search([
		('package_no', '=', self.package_id.name),
			('move_type', '=', 'out_invoice'),   # Sale invoice
			('state', '=', 'posted')
		], limit=1)

		if existing_invoice:
			credit_notes = self.env['account.move'].search([
				('reversed_entry_id', '=', existing_invoice.id),
				('move_type', '=', 'out_refund'),   # credit note
				('state', '=', 'posted')
			], limit=1)

			if not credit_notes:
				raise ValidationError(
					f"A posted invoice ({existing_invoice.name}) already exists for {self.package_id.name}. ""You must issue a credit note first for the original invoice before cancel the Booking.")

		for inv in invoices:
			payments = self.env['account.payment'].search([('memo','=',inv.name),('payment_type','=','outbound')])
			if inv.state == 'posted':
				inv.button_draft()
				inv.button_cancel()
			if inv.state == 'draft':
				inv.button_cancel()
			if self.create_vendor_refund:
				for payment in payments:
					payment.action_draft()
					payment.action_cancel()
		# 	self.package_id.create_bill_of_vendor_func('in_refund')

		# creating invoices and bills for cancelation charges
		line_ids = []

		cancelation_product = self.env['product.product'].search([('name','=','Cancelation Service')])
		if not cancelation_product:
			raise ValidationError("Please Create Cancelation Product with name: 'Cancelation Service'")

		journal_id = self.env['account.journal'].search([('type','=','sale')],limit=1)

		account_id = self.env['account.account'].search([('sale','=',True)], limit=1)

		if self.cancelation_charges:
			line_ids.append(
				(0,0, {
				'name':"Cancelation Charges",
				'quantity':1,
				'price_unit':self.cancelation_charges,
				'account_id':account_id.id,
				'product_id':cancelation_product.id,
				'journal_id':journal_id.id,
				})
				)
		if line_ids:
			invoice_vals = {
				'invoice_date': datetime.today(),
				'move_type': 'out_invoice',
				'partner_id': self.package_id.partner_id.id,
				# 'invoice_payment_term_id': self.package_id.payment_term_id.id or False,
				'journal_id':journal_id.id,
				'package_no': self.package_id.name,
				'payment_term': self.package_id.payment_term,
				'payment_date_custom': self.package_id.payment_date_custom,
				# 'ref': ref,
				'invoice_origin': self.package_id.name,
				# 'account_id':account_id.id,
				'invoice_line_ids': line_ids,
			}
		# sudo ssh root@5.189.175.68
			if invoice_vals:
				move = self.env['account.move'].with_context(default_move_type='out_invoice').create(invoice_vals)


		# creating cancelation bills
	# if self.include_vendor_charges:
		line_ids = []
		uniq_vendors= []
		currency_id=0
		if self.package_id.itinarnay_package:
			for rec in self.package_id.itinarnay_package:
				if rec.supplier.id not in uniq_vendors: 
					uniq_vendors.append(rec.supplier.id)
		# ---------------------------------
		journal_id = self.env['account.journal'].search([('type','=','purchase')],limit=1)
		for j in uniq_vendors:
			service_lines = self.env['all.services'].search([('supplier','=',j),('itinarnay_return','=',self.package_id.id)])
			account_id = self.env['account.account'].search([('purchase','=',True)], limit=1)
			if not account_id:
				raise ValidationError("Please Select Purchase Account")
			charges = 0
			cancel_tree_rec = self.env['cancel.charge'].search([('partner_id','=',j),('cancel_rel','=',self.package_id.id)])
			for c in cancel_tree_rec:
				charges = c.charges
				if charges:
					line_ids.append(
						(0,0, {
							'name':"Cancelation Charges"+", "+self.package_id.name,
							'quantity':1,
							'price_unit':charges,
							'account_id':account_id.id,
							'product_id':cancelation_product.id or None,
							'journal_id':journal_id.id,
							})
						)

			if line_ids:
				invoice_vals = {
					'invoice_date': datetime.today(),
					# 'account_id':account_id.id,
					'move_type': 'in_invoice',
					'partner_id': j,
					'invoice_origin': self.package_id.name,
					# 'invoice_payment_term_id': self.package_id.payment_term_id.id or False,
					'package_no': self.package_id.name,
					'payment_term': self.package_id.payment_term,
					'payment_date_custom': self.package_id.payment_date_custom,
					'journal_id': journal_id.id,
					'invoice_line_ids': line_ids,
				}
				# if invoice_vals:
				move = self.env['account.move'].with_context(default_type='in_invoice').create(invoice_vals)



