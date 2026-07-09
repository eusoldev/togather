#-*- coding:utf-8 -*-
from odoo import models, fields, api,_



class AccMoveLineDataSetExt(models.Model):
	_inherit = 'account.move.line'

	def set_accounts(self):
		sql = "UPDATE account_move_line SET account_id = '%s' WHERE journal_id = '%s' and account_id = '%s'" % ('70','9', '67')
		self._cr.execute(sql)
		self._cr.commit()


class AccPaymentPackageDataSet(models.Model):
	_inherit = 'account.payment'

	def set_payments(self):
		for rec in self.search([('journal_entry','!=',False)]):

			lab = str(rec.amount)+' @ '+str(rec.journal_id.bank_charge_amt)+"-"+rec.name
			for x in rec.journal_entry.line_ids:
				x.update({
					'name':lab,
					})


class SOPackageDataSet(models.Model):
	_inherit = 'all.services'

	def set_e_ticket_data(self):
		for pkg in self.search([]):
			tickets_list = []
			if pkg.e_ticket:
				rec = self.env['electronic.ticket'].search([('name','=',pkg.e_ticket)], limit=1)
				if not rec:
					ticket = self.env['electronic.ticket'].create({
						'name':pkg.e_ticket
						})
					tickets_list.append(ticket.id)
				else:
					tickets_list.append(rec.id)

			pkg.update({
				'e_ticket_m2m':[(6,0,tickets_list)]
				})



class SOPackageDataSet(models.Model):
	_inherit = 'reservation.order'

	def set_links_data(self):
		for pkg in self.search([]):
			# if pkg.id == 50:
			print ("11111111111111")
			print (pkg.itinarnay_package)
			for line in pkg.itinarnay_package:
				move_line = self.env['account.move.line'].search([('move_id.invoice_origin','like',pkg.name),('move_id.state','!=','cancel'),('move_id.type','=','in_invoice')])
				print (move_line)
				print (move_line.move_id)

				for m_line in move_line:
					if not line.bill_id:
					# if m_line.price_subtotal == line.price or m_line.price_subtotal == line.price:
						if m_line.date_from == line.date_from and m_line.date_to == line.date_to:
							print ("0000000000000000000000000")
							print (m_line)
							line.write({
								'bill_id':m_line.move_id.id,
								})
							print ("11111111111111111111111111111")


	def set_arrival_departure_dates(self):
		for rec in self.search([]):
			invoices = self.env['account.move'].search([('invoice_origin', 'like', rec.name)])

			for x in invoices:
				if not x.arrival_date and not x.departure_date:

					x.write({
						'arrival_date':rec.arrival_date,
						'departure_date':rec.departure_date,
						})


	def set_check_in_out_date(self):
		for pkg in self.search([]):
			# if pkg.name == 'RQ-00108':
			print (pkg.name)
			for line in pkg.itinarnay_package:
				move_line = self.env['account.move.line'].search([('move_id.package_no','=',pkg.name),('move_id.state','!=','cancel')])
				print (move_line)
				print (move_line.move_id)

				for m_line in move_line:
					print ("222222222222222222222222222222")
					print (m_line.price_subtotal)
					print (line.price)
					print (m_line.price_subtotal)
					if m_line.price_subtotal == round(line.price,2) or m_line.price_subtotal == line.price:
						print ("0000000000000000000000000")
						print (m_line.date_from)
						print (m_line.date_to)
						m_line.write({
							'date_from':line.date_from,
							'date_to':line.date_to,
							})
						print (m_line.date_from)
						print (m_line.date_to)
						print ("11111111111111111111111111111")

	def set_invoice_dates(self):
		for pkg in self.search([]):
			invoices = self.env['account.move'].search([("invoice_origin",'=',pkg.name)])
			for inv in invoices:
				if inv.state == "posted":
					inv.button_cancel()
					inv.invoice_date = pkg.arrival_date

					for pkg_line in pkg.itinarnay_package:
						for m_line in inv.invoice_line_ids:
							if m_line.price_subtotal == pkg_line.price or m_line.price_subtotal == pkg_line.total:
								if not m_line.date_from or m_line.date_to:
									m_line.write({
										'date_from':pkg_line.date_from,
										'date_to':pkg_line.date_to,
										})



				if inv.state == "draft":
					inv.invoice_date = pkg.arrival_date
					for pkg_line in pkg.itinarnay_package:
						for m_line in inv.invoice_line_ids:
							if m_line.price_subtotal == pkg_line.price or m_line.price_subtotal == pkg_line.total:
								m_line.write({
									'date_from':pkg_line.date_from,
									'date_to':pkg_line.date_to,
									})

				inv.button_draft()
				inv.action_post()




# itinarnay_return

