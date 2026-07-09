#-*- coding:utf-8 -*-
########################################################################################
########################################################################################
##                                                                                    ##
##    OpenERP, Open Source Management Solution                                        ##
##    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved       ##
##                                                                                    ##
##    This program is free software: you can redistribute it and/or modify            ##
##    it under the terms of the GNU Affero General Public License as published by     ##
##    the Free Software Foundation, either version 3 of the License, or               ##
##    (at your option) any later version.                                             ##
##                                                                                    ##
##    This program is distributed in the hope that it will be useful,                 ##
##    but WITHOUT ANY WARRANTY; without even the implied warranty of                  ##
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                   ##
##    GNU Affero General Public License for more details.                             ##
##                                                                                    ##
##    You should have received a copy of the GNU Affero General Public License        ##
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.           ##
##                                                                                    ##
########################################################################################
########################################################################################

from odoo import api, models, fields
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import datetime
from datetime import date
from datetime import date, timedelta
import datetime
from dateutil.relativedelta import *
import math
from PIL import Image, ImageDraw
import xlsxwriter



class dmc_report(models.AbstractModel):
	_name = 'report.dmc_report.dmc_report'
	_description = 'DMC PDF Report'

	@api.model
	def _get_report_values(self, docids, data=None):
		record_wizard = self.env['dmc.report'].browse(self.env.context.get('active_ids'))

		form = record_wizard.form
		to = record_wizard.to
		typee = record_wizard.typee
		partner_id = record_wizard.partner_id
		company = record_wizard.company_id
		report_type = record_wizard.report_type
		country_id = record_wizard.country_id
		booking_type = record_wizard.booking_type


		if typee == 'all':
			if report_type == 'vendor':
				partner = self.env['res.partner'].sudo().search([('dmc','=',True)])
			if report_type == 'hotel':
				partner = self.env['res.partner'].sudo().search([('dmc','=',True)])
			if report_type == 'destination':
				partner = self.env['destination.name'].sudo().search([])
		else:
			partner = []
			if report_type == 'hotel':
				for x in partner_id:
					partner.append(x)

			if report_type == 'vendor':
				for x in partner_id:
					partner.append(x)

			if report_type == 'destination':
				for x in country_id:
					partner.append(x)



		all_part_selected = []
		all_part_selected_2 = []
		
		hotel_main_list = []
		hotel_summary_list = []
		for x in partner:

			all_part_selected.append([x.id])
			all_part_selected_2.append(x.id)
			if report_type == 'vendor':
				hot_dest = ('partner_id','=',x.id)
				record = self.env['account.move'].sudo().search([('date','>=',form),('date','<=',to),hot_dest,('state','=','posted'),('move_type','=','in_invoice')])

			if report_type == 'destination':
				hot_dest = ('partner_id.country_id','=',x.id)
				record = self.env['account.move'].sudo().search([('date','>=',form),('date','<=',to),hot_dest,('state','=','posted'),('move_type','=','in_invoice')])


			if report_type == 'hotel':
				all_sales_services = self.env['all.services'].sudo().search([('product_id','=',2),('hotel_id', '=',x.id)])


				pkgs_list = []
				for service in all_sales_services:
					if service.hotel_return.stages == 'validate':
						if service.hotel_return.name not in pkgs_list:
							pkgs_list.append(service.hotel_return.name)



				record = self.env['account.move'].sudo().search([('date','>=',form),('date','<=',to),('invoice_origin','in',pkgs_list),('state','=','posted'),('move_type','=','in_invoice')])

			main_list = []
			pkg_total = 0
			serial_total = 0
			for inv in record:


				if report_type == 'hotel':
					if inv.hotel_ids.ids in all_part_selected:
						serial_total += 1

				else:
					serial_total += 1

				package = self.env['reservation.order'].sudo().search([('name','=',inv.invoice_origin)])
				date_from = ""
				date_to = ""
				currency = ""
				nights = 0
				amnt_fc = 0
				currency_fc=0
				for hotel in package.hotel_pkg:

					if booking_type =='arrival_date':
							if hotel.hotel_return.arrival_date >= form and hotel.hotel_return.arrival_date <= to: 

								if report_type == 'hotel':
									if inv.hotel_ids.ids in all_part_selected and hotel.hotel_id.id in all_part_selected_2:


										customer_name = []
										room_type_list = []
										for t in hotel.room_type:
											room_type_list.append(t.name)

										if hotel.customer_m2m:
											for y in hotel.customer_m2m:
												customer_name.append(y.name)


										amnt_fc += hotel.amnt_fc
										# currency_fc += hotel.currency_fc
										nights += hotel.nights*hotel.room_qty
										if not date_from:
											date_from = hotel.date_from
										else:
											date_from = str(date_from)+"/"+str(hotel.date_from)
										if not date_to:
											date_to = hotel.date_to
										else:
											date_to = str(date_to)+"/"+str(hotel.date_to)
										if not currency:
											currency = hotel.currency_name.name
										else:
											currency = str(currency)+"/"+str(hotel.currency_name.name)

										if inv.amount_total:
											if report_type == 'hotel':
												all_hotels = []
												for ah in inv.hotel_ids:
													if ah.id == x.id:
														all_hotels.append(ah.name)

												Hotel_name = all_hotels
											if report_type == 'vendor':
												Hotel_name = inv.partner_id.name
											if report_type == 'destination':
												Hotel_name = inv.partner_id.country_id.name

											main_list.append({
												'Invoice_no':inv.name,
												'date_order':hotel.hotel_return.date_order,
												'arrival_date':hotel.hotel_return.arrival_date,
												'customer_name':customer_name,
												'room_type':room_type_list,
												'no_of_guest':hotel.no_of_person,
												'rq_number':inv.package_no,
												'Hotel_name':Hotel_name,
												'check_in':date_from,
												'check_out':date_to,
												'nights':nights,
												'amount_fc':amnt_fc,
												'currency_id':currency,
												'toatal_pkage_amount':inv.amount_total,
												'creation_date':package.create_date,
												'sale_person':package.user_id.name,
												'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
												})
											pkg_total += inv.amount_total
									
								else:


									customer_name = []
									room_type_list = []
									for t in hotel.room_type:
										room_type_list.append(t.name)

									if hotel.customer_m2m:
										for y in hotel.customer_m2m:
											customer_name.append(y.name)


									amnt_fc += hotel.amnt_fc
									# currency_fc += hotel.currency_fc
									nights += hotel.nights*hotel.room_qty
									if not date_from:
										date_from = hotel.date_from
									else:
										date_from = str(date_from)+"/"+str(hotel.date_from)
									if not date_to:
										date_to = hotel.date_to
									else:
										date_to = str(date_to)+"/"+str(hotel.date_to)
									if not currency:
										currency = hotel.currency_name.name
									else:
										currency = str(currency)+"/"+str(hotel.currency_name.name)

									if inv.amount_total:
										if report_type == 'hotel':
											all_hotels = []
											for ah in inv.hotel_ids:
												if ah.id == x.id:
													all_hotels.append(ah.name)

											Hotel_name = all_hotels
										if report_type == 'vendor':
											Hotel_name = inv.partner_id.name
										if report_type == 'destination':
											Hotel_name = inv.partner_id.country_id.name
										main_list.append({
											'Invoice_no':inv.name,
											'date_order':hotel.hotel_return.date_order,
											'arrival_date':hotel.hotel_return.arrival_date,
											'customer_name':customer_name,
											'room_type':room_type_list,
											'no_of_guest':hotel.no_of_person,
											'rq_number':inv.package_no,
											'Hotel_name':Hotel_name,
											'get_Hotel_name':hotel.hotel_id.name,
											'check_in':date_from,
											'check_out':date_to,
											'nights':nights,
											'amount_fc':amnt_fc,
											'currency_id':currency,
											'toatal_pkage_amount':inv.amount_total,
											'creation_date':package.create_date,
											'sale_person':package.user_id.name,
											'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
											})
										pkg_total += inv.amount_total




					if booking_type =='book_date':
							if hotel.hotel_return.date_order.date() >= form and hotel.hotel_return.date_order.date() <= to: 

								if report_type == 'hotel':
									if inv.hotel_ids.ids in all_part_selected and hotel.hotel_id.id in all_part_selected_2:


										customer_name = []
										room_type_list = []
										for t in hotel.room_type:
											room_type_list.append(t.name)

										if hotel.customer_m2m:
											for y in hotel.customer_m2m:
												customer_name.append(y.name)


										amnt_fc += hotel.amnt_fc
										# currency_fc += hotel.currency_fc
										nights += hotel.nights*hotel.room_qty
										if not date_from:
											date_from = hotel.date_from
										else:
											date_from = str(date_from)+"/"+str(hotel.date_from)
										if not date_to:
											date_to = hotel.date_to
										else:
											date_to = str(date_to)+"/"+str(hotel.date_to)
										if not currency:
											currency = hotel.currency_name.name
										else:
											currency = str(currency)+"/"+str(hotel.currency_name.name)

										if inv.amount_total:
											if report_type == 'hotel':
												all_hotels = []
												for ah in inv.hotel_ids:
													if ah.id == x.id:
														all_hotels.append(ah.name)

												Hotel_name = all_hotels
											if report_type == 'vendor':
												Hotel_name = inv.partner_id.name
											if report_type == 'destination':
												Hotel_name = inv.partner_id.country_id.name

											main_list.append({
												'Invoice_no':inv.name,
												'date_order':hotel.hotel_return.date_order,
												'arrival_date':hotel.hotel_return.arrival_date,
												'customer_name':customer_name,
												'room_type':room_type_list,
												'no_of_guest':hotel.no_of_person,
												'rq_number':inv.package_no,
												'Hotel_name':Hotel_name,
												'check_in':date_from,
												'check_out':date_to,
												'nights':nights,
												'amount_fc':amnt_fc,
												'currency_id':currency,
												'toatal_pkage_amount':inv.amount_total,
												'creation_date':package.create_date,
												'sale_person':package.user_id.name,
												'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
												})
											pkg_total += inv.amount_total
								else:
									customer_name = []
									room_type_list = []
									for t in hotel.room_type:
										room_type_list.append(t.name)

									if hotel.customer_m2m:
										for y in hotel.customer_m2m:
											customer_name.append(y.name)


									amnt_fc += hotel.amnt_fc
									nights += hotel.nights*hotel.room_qty
									if not date_from:
										date_from = hotel.date_from
									else:
										date_from = str(date_from)+"/"+str(hotel.date_from)
									if not date_to:
										date_to = hotel.date_to
									else:
										date_to = str(date_to)+"/"+str(hotel.date_to)
									if not currency:
										currency = hotel.currency_name.name
									else:
										currency = str(currency)+"/"+str(hotel.currency_name.name)

									if inv.amount_total:
										if report_type == 'hotel':
											all_hotels = []
											for ah in inv.hotel_ids:
												if ah.id == x.id:
													all_hotels.append(ah.name)

											Hotel_name = all_hotels
										if report_type == 'vendor':
											Hotel_name = inv.partner_id.name
										if report_type == 'destination':
											Hotel_name = inv.partner_id.country_id.name


										main_list.append({
											'Invoice_no':inv.name,
											'date_order':hotel.hotel_return.date_order,
											'arrival_date':hotel.hotel_return.arrival_date,
											'customer_name':customer_name,
											'room_type':room_type_list,
											'get_Hotel_name':hotel.hotel_id.name,
											'no_of_guest':hotel.no_of_person,
											'rq_number':inv.package_no,
											'Hotel_name':Hotel_name,
											'check_in':date_from,
											'check_out':date_to,
											'nights':nights,
											'amount_fc':amnt_fc,
											'currency_id':currency,
											'toatal_pkage_amount':inv.amount_total,
											'creation_date':package.create_date,
											'sale_person':package.user_id.name,
											'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
											})
										pkg_total += inv.amount_total




					if booking_type !='book_date' and booking_type !='arrival_date' :
				 
							if report_type == 'hotel':
								if inv.hotel_ids.ids in all_part_selected and hotel.hotel_id.id in all_part_selected_2:


									customer_name = []
									room_type_list = []
									for t in hotel.room_type:
										room_type_list.append(t.name)

									if hotel.customer_m2m:
										for y in hotel.customer_m2m:
											customer_name.append(y.name)


									amnt_fc += hotel.amnt_fc
									# currency_fc += hotel.currency_fc
									nights += hotel.nights*hotel.room_qty
									if not date_from:
										date_from = hotel.date_from
									else:
										date_from = str(date_from)+"/"+str(hotel.date_from)
									if not date_to:
										date_to = hotel.date_to
									else:
										date_to = str(date_to)+"/"+str(hotel.date_to)
									if not currency:
										currency = hotel.currency_name.name
									else:
										currency = str(currency)+"/"+str(hotel.currency_name.name)

									if inv.amount_total:
										if report_type == 'hotel':
											all_hotels = []
											for ah in inv.hotel_ids:
												if ah.id == x.id:
													all_hotels.append(ah.name)

											Hotel_name = all_hotels
										if report_type == 'vendor':
											Hotel_name = inv.partner_id.name
										if report_type == 'destination':
											Hotel_name = inv.partner_id.country_id.name

										main_list.append({
											'Invoice_no':inv.name,
											'date_order':hotel.hotel_return.date_order,
											'arrival_date':hotel.hotel_return.arrival_date,
											'customer_name':customer_name,
											'room_type':room_type_list,
											'no_of_guest':hotel.no_of_person,
											'rq_number':inv.package_no,
											'Hotel_name':Hotel_name,
											'check_in':date_from,
											'check_out':date_to,
											'nights':nights,
											'amount_fc':amnt_fc,
											'currency_id':currency,
											'toatal_pkage_amount':inv.amount_total,
											'creation_date':package.create_date,
											'sale_person':package.user_id.name,
											'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
											})
										pkg_total += inv.amount_total
								

							else:


								customer_name = []
								room_type_list = []
								for t in hotel.room_type:
									room_type_list.append(t.name)

								if hotel.customer_m2m:
									for y in hotel.customer_m2m:
										customer_name.append(y.name)


								amnt_fc += hotel.amnt_fc
								# currency_fc += hotel.currency_fc
								nights += hotel.nights*hotel.room_qty
								if not date_from:
									date_from = hotel.date_from
								else:
									date_from = str(date_from)+"/"+str(hotel.date_from)
								if not date_to:
									date_to = hotel.date_to
								else:
									date_to = str(date_to)+"/"+str(hotel.date_to)
								if not currency:
									currency = hotel.currency_name.name
								else:
									currency = str(currency)+"/"+str(hotel.currency_name.name)

								if inv.amount_total:
									if report_type == 'hotel':
										all_hotels = []
										for ah in inv.hotel_ids:
											if ah.id == x.id:
												all_hotels.append(ah.name)

										Hotel_name = all_hotels
									if report_type == 'vendor':
										Hotel_name = inv.partner_id.name
									if report_type == 'destination':
										Hotel_name = inv.partner_id.country_id.name

									
									main_list.append({
										'Invoice_no':inv.name,
										'date_order':hotel.hotel_return.date_order,
										'arrival_date':hotel.hotel_return.arrival_date,
										'customer_name':customer_name,
										'room_type':room_type_list,
										'get_Hotel_name':hotel.hotel_id.name,
										'no_of_guest':hotel.no_of_person,
										'rq_number':inv.package_no,
										'Hotel_name':Hotel_name,
										'check_in':date_from,
										'check_out':date_to,
										'nights':nights,
										'amount_fc':amnt_fc,
										'currency_id':currency,
										'toatal_pkage_amount':inv.amount_total,
										'creation_date':package.create_date,
										'sale_person':package.user_id.name,
										'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
										})
									pkg_total += inv.amount_total







			if pkg_total > 0:
				hotel_summary_list.append({
					'hotel_name':x.name,
					# 'destination':destination_list,
					'pkg_total':pkg_total,
					})

			if main_list:
				hotel_main_list.append({
					'hotel':x.name,
					# 'destination':destination_list,
					'serial_total':serial_total,
					'main_list':main_list,
					})



		return {
			'doc_ids': docids,
			'doc_model':'account.move',
			'form': form,
			'to': to,
			'report_type': report_type,
			'company': company,
			'hotel_main_list': hotel_main_list,
			'hotel_summary_list': hotel_summary_list,
		}




class dmc_report_xlsx(models.AbstractModel):
	_name = 'report.dmc_report.dmc_report_xlsx'

	_inherit = 'report.report_xlsx.abstract'
	_description="DMC Report"





	def generate_xlsx_report(self, workbook, data, wizard_obj):
		record_wizard = self.env['dmc.report'].browse(self.env.context.get('active_ids'))
		form = record_wizard.form
		to = record_wizard.to
		typee = record_wizard.typee
		partner_id = record_wizard.partner_id
		company = record_wizard.company_id
		country_id = record_wizard.country_id
		report_type = record_wizard.report_type
		booking_type = record_wizard.booking_type

		################################ caculated values for excel report ##########
		############################################################################

		if typee == 'all':
			if report_type == 'vendor':
				partner = self.env['res.partner'].sudo().search([('dmc','=',True)]) 
			if report_type == 'hotel':
				partner = self.env['res.partner'].sudo().search([('dmc','=',True)])
			if report_type == 'destination':
				partner = self.env['destination.name'].sudo().search([])
		else:
			partner = []
			if report_type == 'vendor':
				for x in partner_id:
					partner.append(x)

			if report_type == 'hotel':
				for x in partner_id:
					partner.append(x)

			if report_type == 'destination':
				for x in country_id:
					partner.append(x)


		all_part_selected = []
		all_part_selected_2 = []
		
		hotel_main_list = []
		hotel_summary_list = []
		for x in partner:

			all_part_selected.append([x.id])
			all_part_selected_2.append(x.id)

			if report_type == 'vendor':
				hot_dest = ('partner_id','=',x.id)
				record = self.env['account.move'].sudo().search([('date','>=',form),('date','<=',to),hot_dest,('state','=','posted'),('move_type','=','in_invoice')])

			if report_type == 'destination':
				hot_dest = ('partner_id.country_id','=',x.id)
				record = self.env['account.move'].sudo().search([('date','>=',form),('date','<=',to),hot_dest,('state','=','posted'),('move_type','=','in_invoice')])


			if report_type == 'hotel':
				all_sales_services = self.env['all.services'].sudo().search([('product_id','=',2),('hotel_id', '=',x.id)])

				pkgs_list = []
				for service in all_sales_services:
					if service.hotel_return.stages == 'validate':
						if service.hotel_return.name not in pkgs_list:
							pkgs_list.append(service.hotel_return.name)

				record = self.env['account.move'].sudo().search([('date','>=',form),('date','<=',to),('invoice_origin','in',pkgs_list),('state','=','posted'),('move_type','=','in_invoice')])



			main_list = []
			pkg_total = 0
			serial_total = 0
			for inv in record:
				if report_type == 'hotel':
					if inv.hotel_ids.ids in all_part_selected:
						serial_total += 1

				else:
					serial_total += 1

				serial_total += 1
				package = self.env['reservation.order'].sudo().search([('name','=',inv.invoice_origin)])
				date_from = ""
				date_to = ""
				currency = ""
				nights = 0
				amnt_fc = 0
				currency_fc=0

				for hotel in package.hotel_pkg:


					if booking_type =='arrival_date':
						
						if hotel.hotel_return.arrival_date >= form and hotel.hotel_return.arrival_date <= to: 
							if report_type == 'hotel':
								if inv.hotel_ids.ids in all_part_selected and hotel.hotel_id.id in all_part_selected_2:


									customer_name = []
									room_type_list = []
									for t in hotel.room_type:
										room_type_list.append(t.name)

									if hotel.customer_m2m:
										for y in hotel.customer_m2m:
											customer_name.append(y.name)


									amnt_fc += hotel.amnt_fc
									# currency_fc += hotel.currency_fc
									nights += hotel.nights*hotel.room_qty
									if not date_from:
										date_from = hotel.date_from
									else:
										date_from = str(date_from)+"/"+str(hotel.date_from)
									if not date_to:
										date_to = hotel.date_to
									else:
										date_to = str(date_to)+"/"+str(hotel.date_to)
									if not currency:
										currency = hotel.currency_name.name
									else:
										currency = str(currency)+"/"+str(hotel.currency_name.name)

									if inv.amount_total:
										if report_type == 'hotel':
											all_hotels = []
											for ah in inv.hotel_ids:
												if ah.id == x.id:
													all_hotels.append(ah.name)

											Hotel_name = all_hotels
										if report_type == 'vendor':
											Hotel_name = inv.partner_id.name
										if report_type == 'destination':
											Hotel_name = inv.partner_id.country_id.name

										
										main_list.append({
											'Invoice_no':inv.name,
											'date_order':hotel.hotel_return.date_order,
											'arrival_date':hotel.hotel_return.arrival_date,
											'customer_name':customer_name,
											'room_type':room_type_list,
											'no_of_guest':hotel.no_of_person,
											'rq_number':inv.package_no,
											'Hotel_name':Hotel_name,
											'check_in':date_from,
											'check_out':date_to,
											'nights':nights,
											'amount_fc':amnt_fc,
											'currency_id':currency,
											'toatal_pkage_amount':inv.amount_total,
											'creation_date':package.create_date,
											'sale_person':package.user_id.name,
											'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
											})
										pkg_total += inv.amount_total
								
							else:


								customer_name = []
								room_type_list = []
								for t in hotel.room_type:
									room_type_list.append(t.name)

								if hotel.customer_m2m:
									for y in hotel.customer_m2m:
										customer_name.append(y.name)


								amnt_fc += hotel.amnt_fc
								# currency_fc += hotel.currency_fc
								nights += hotel.nights*hotel.room_qty
								if not date_from:
									date_from = hotel.date_from
								else:
									date_from = str(date_from)+"/"+str(hotel.date_from)
								if not date_to:
									date_to = hotel.date_to
								else:
									date_to = str(date_to)+"/"+str(hotel.date_to)
								if not currency:
									currency = hotel.currency_name.name
								else:
									currency = str(currency)+"/"+str(hotel.currency_name.name)

								if inv.amount_total:
									if report_type == 'hotel':
										all_hotels = []
										for ah in inv.hotel_ids:
											if ah.id == x.id:
												all_hotels.append(ah.name)

										Hotel_name = all_hotels
									if report_type == 'vendor':
										Hotel_name = inv.partner_id.name
									if report_type == 'destination':
										Hotel_name = inv.partner_id.country_id.name

									
									main_list.append({
										'Invoice_no':inv.name,
										'date_order':hotel.hotel_return.date_order,
										'arrival_date':hotel.hotel_return.arrival_date,
										'get_Hotel_name':hotel.hotel_id.name,
										'customer_name':customer_name,
										'room_type':room_type_list,
										'no_of_guest':hotel.no_of_person,
										'rq_number':inv.package_no,
										'Hotel_name':Hotel_name,
										'check_in':date_from,
										'check_out':date_to,
										'nights':nights,
										'amount_fc':amnt_fc,
										'currency_id':currency,
										'toatal_pkage_amount':inv.amount_total,
										'creation_date':package.create_date,
										'sale_person':package.user_id.name,
										'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
										})
									pkg_total += inv.amount_total



			
					if booking_type =='book_date':
						
						if hotel.hotel_return.date_order.date() >= form and hotel.hotel_return.date_order.date() <= to: 
							if report_type == 'hotel':
								if inv.hotel_ids.ids in all_part_selected and hotel.hotel_id.id in all_part_selected_2:


									customer_name = []
									room_type_list = []
									for t in hotel.room_type:
										room_type_list.append(t.name)

									if hotel.customer_m2m:
										for y in hotel.customer_m2m:
											customer_name.append(y.name)


									amnt_fc += hotel.amnt_fc
									# currency_fc += hotel.currency_fc
									nights += hotel.nights*hotel.room_qty
									if not date_from:
										date_from = hotel.date_from
									else:
										date_from = str(date_from)+"/"+str(hotel.date_from)
									if not date_to:
										date_to = hotel.date_to
									else:
										date_to = str(date_to)+"/"+str(hotel.date_to)
									if not currency:
										currency = hotel.currency_name.name
									else:
										currency = str(currency)+"/"+str(hotel.currency_name.name)

									if inv.amount_total:
										if report_type == 'hotel':
											all_hotels = []
											for ah in inv.hotel_ids:
												if ah.id == x.id:
													all_hotels.append(ah.name)

											Hotel_name = all_hotels
										if report_type == 'vendor':
											Hotel_name = inv.partner_id.name
										if report_type == 'destination':
											Hotel_name = inv.partner_id.country_id.name

										
										main_list.append({
											'Invoice_no':inv.name,
											'date_order':hotel.hotel_return.date_order,
											'arrival_date':hotel.hotel_return.arrival_date,
											'customer_name':customer_name,
											'room_type':room_type_list,
											'no_of_guest':hotel.no_of_person,
											'rq_number':inv.package_no,
											'Hotel_name':Hotel_name,
											'check_in':date_from,
											'check_out':date_to,
											'nights':nights,
											'amount_fc':amnt_fc,
											'currency_id':currency,
											'toatal_pkage_amount':inv.amount_total,
											'creation_date':package.create_date,
											'sale_person':package.user_id.name,
											'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
											})
										pkg_total += inv.amount_total
								

							else:


								customer_name = []
								room_type_list = []
								for t in hotel.room_type:
									room_type_list.append(t.name)

								if hotel.customer_m2m:
									for y in hotel.customer_m2m:
										customer_name.append(y.name)


								amnt_fc += hotel.amnt_fc
								# currency_fc += hotel.currency_fc
								nights += hotel.nights*hotel.room_qty
								if not date_from:
									date_from = hotel.date_from
								else:
									date_from = str(date_from)+"/"+str(hotel.date_from)
								if not date_to:
									date_to = hotel.date_to
								else:
									date_to = str(date_to)+"/"+str(hotel.date_to)
								if not currency:
									currency = hotel.currency_name.name
								else:
									currency = str(currency)+"/"+str(hotel.currency_name.name)

								if inv.amount_total:
									if report_type == 'hotel':
										all_hotels = []
										for ah in inv.hotel_ids:
											if ah.id == x.id:
												all_hotels.append(ah.name)

										Hotel_name = all_hotels
									if report_type == 'vendor':
										Hotel_name = inv.partner_id.name
									if report_type == 'destination':
										Hotel_name = inv.partner_id.country_id.name

									
									main_list.append({
										'Invoice_no':inv.name,
										'get_Hotel_name':hotel.hotel_id.name,
										'date_order':hotel.hotel_return.date_order,
										'arrival_date':hotel.hotel_return.arrival_date,
										'customer_name':customer_name,
										'room_type':room_type_list,
										'no_of_guest':hotel.no_of_person,
										'rq_number':inv.package_no,
										'Hotel_name':Hotel_name,
										'check_in':date_from,
										'check_out':date_to,
										'nights':nights,
										'amount_fc':amnt_fc,
										'currency_id':currency,
										'toatal_pkage_amount':inv.amount_total,
										'creation_date':package.create_date,
										'sale_person':package.user_id.name,
										'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
										})
									pkg_total += inv.amount_total



			
					if  booking_type !='book_date' and booking_type !='arrival_date' :
						
						if report_type == 'hotel':
							if inv.hotel_ids.ids in all_part_selected and hotel.hotel_id.id in all_part_selected_2:


								customer_name = []
								room_type_list = []
								for t in hotel.room_type:
									room_type_list.append(t.name)

								if hotel.customer_m2m:
									for y in hotel.customer_m2m:
										customer_name.append(y.name)


								amnt_fc += hotel.amnt_fc
								# currency_fc += hotel.currency_fc
								nights += hotel.nights*hotel.room_qty
								if not date_from:
									date_from = hotel.date_from
								else:
									date_from = str(date_from)+"/"+str(hotel.date_from)
								if not date_to:
									date_to = hotel.date_to
								else:
									date_to = str(date_to)+"/"+str(hotel.date_to)
								if not currency:
									currency = hotel.currency_name.name
								else:
									currency = str(currency)+"/"+str(hotel.currency_name.name)

								if inv.amount_total:
									if report_type == 'hotel':
										all_hotels = []
										for ah in inv.hotel_ids:
											if ah.id == x.id:
												all_hotels.append(ah.name)

										Hotel_name = all_hotels
									if report_type == 'vendor':
										Hotel_name = inv.partner_id.name
									if report_type == 'destination':
										Hotel_name = inv.partner_id.country_id.name

									
									main_list.append({
										'Invoice_no':inv.name,
										'date_order':hotel.hotel_return.date_order,
										'arrival_date':hotel.hotel_return.arrival_date,
										'customer_name':customer_name,
										'room_type':room_type_list,
										'no_of_guest':hotel.no_of_person,
										'rq_number':inv.package_no,
										'Hotel_name':Hotel_name,
										'check_in':date_from,
										'check_out':date_to,
										'nights':nights,
										'amount_fc':amnt_fc,
										'currency_id':currency,
										'toatal_pkage_amount':inv.amount_total,
										'creation_date':package.create_date,
										'sale_person':package.user_id.name,
										'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
										})
									pkg_total += inv.amount_total
							
						else:


							customer_name = []
							room_type_list = []
							for t in hotel.room_type:
								room_type_list.append(t.name)

							if hotel.customer_m2m:
								for y in hotel.customer_m2m:
									customer_name.append(y.name)


							amnt_fc += hotel.amnt_fc
							# currency_fc += hotel.currency_fc
							nights += hotel.nights*hotel.room_qty
							if not date_from:
								date_from = hotel.date_from
							else:
								date_from = str(date_from)+"/"+str(hotel.date_from)
							if not date_to:
								date_to = hotel.date_to
							else:
								date_to = str(date_to)+"/"+str(hotel.date_to)
							if not currency:
								currency = hotel.currency_name.name
							else:
								currency = str(currency)+"/"+str(hotel.currency_name.name)

							if inv.amount_total:
								if report_type == 'hotel':
									all_hotels = []
									for ah in inv.hotel_ids:
										if ah.id == x.id:
											all_hotels.append(ah.name)

									Hotel_name = all_hotels
								if report_type == 'vendor':
									Hotel_name = inv.partner_id.name
								if report_type == 'destination':
									Hotel_name = inv.partner_id.country_id.name

								main_list.append({
									'Invoice_no':inv.name,
									'date_order':hotel.hotel_return.date_order,
									'arrival_date':hotel.hotel_return.arrival_date,
									'customer_name':customer_name,
									'room_type':room_type_list,
									'get_Hotel_name':hotel.hotel_id.name,
									'no_of_guest':hotel.no_of_person,
									'rq_number':inv.package_no,
									'Hotel_name':Hotel_name,
									'check_in':date_from,
									'check_out':date_to,
									'nights':nights,
									'amount_fc':amnt_fc,
									'currency_id':currency,
									'toatal_pkage_amount':inv.amount_total,
									'creation_date':package.create_date,
									'sale_person':package.user_id.name,
									'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
									})
								pkg_total += inv.amount_total



		
		



			if pkg_total > 0:
				hotel_summary_list.append({
					'hotel_name':x.name,
					# 'destination':destination_list,
					'pkg_total':pkg_total,
					})

			if main_list:
				hotel_main_list.append({
					'hotel':x.name,
					# 'destination':destination_list,
					'serial_total':serial_total,
					'main_list':main_list,
					})


		if hotel_summary_list:
			worksheet_hotel_summery = workbook.add_worksheet('Summery Report')
			########################################################################
			#######################################################################
			#####################creating styles and data for summery ##########
			######################################################################
			#######################################################################

			# h3_bold = workbook.add_format({'bold': True, 'align': 'left', 'font_size': 20})
			h4_bold = workbook.add_format({'bold': True, 'align': 'left', 'font_size': 10})
			worksheet_hotel_summery.write(1, 1, company.name, h4_bold)
			worksheet_hotel_summery.write(2, 1, company.street, h4_bold)
			worksheet_hotel_summery.write(3, 1, company.street2, h4_bold)
			worksheet_hotel_summery.write(4, 1, company.city, h4_bold)
			worksheet_hotel_summery.write(5, 1, company.country_id.name, h4_bold)
			worksheet_hotel_summery.write(6, 1, 'CR No:', h4_bold)
			worksheet_hotel_summery.write(6, 2, company.company_registry, h4_bold)
			worksheet_hotel_summery.write(7, 1, 'Ph:', h4_bold)
			worksheet_hotel_summery.write(7, 2, company.phone, h4_bold)
			worksheet_hotel_summery.write(8, 1, 'Company Email:', h4_bold)
			worksheet_hotel_summery.write(8, 2, company.email, h4_bold)
			worksheet_hotel_summery.write(9, 1, 'vat', h4_bold)
			worksheet_hotel_summery.write(9, 2, company.vat, h4_bold)
			cell_format = workbook.add_format({'align': 'centre', 'font_size': 15, 'underline': True})
			worksheet_hotel_summery.set_row(10, 25)
			worksheet_hotel_summery.write(11, 1, 'DMC Report', cell_format)
			date_format = workbook.add_format({'align': 'centre', 'font_size': 13, 'underline': True})
			date = 'From: '+str(form)+' TO: '+ str(to)
			worksheet_hotel_summery.merge_range(11, 1,11, 4, 'DMC Report',cell_format)
			worksheet_hotel_summery.write(12, 1, date,date_format)
			worksheet_hotel_summery.merge_range(12, 1,12, 4, date,date_format)

			cell_format = workbook.add_format({'align': 'centre', 'font_size': 10,
											   'underline': True, 'bold': True, 'fg_color': '#DAD7DD',
											   'text_wrap': True})

			merge_format = workbook.add_format({
				'bold': 1,
				'align': 'left',
				'valign': 'vcenter',
				'fg_color': '#DAD7DD'
			})

			worksheet_hotel_summery.set_row(14, 40)
			if report_type == 'hotel':
				worksheet_hotel_summery.write(14, 1, 'Hotel Name', cell_format)
			if report_type == 'vendor':
				worksheet_hotel_summery.write(14, 1, 'Vendor Name', cell_format)
			if report_type == 'destination':
				worksheet_hotel_summery.write(14, 1, 'Destination Name', cell_format)

			if report_type == 'hotel':
				worksheet_hotel_summery.merge_range(14, 1,14, 3, 'Hotel Name',cell_format)

			if report_type == 'vendor':
				worksheet_hotel_summery.merge_range(14, 1,14, 3, 'Vendor Name',cell_format)
				
			if report_type == 'destination':
				worksheet_hotel_summery.merge_range(14, 1,14, 3, 'Destination Name',cell_format)
			# worksheet_hotel_summery.write(14, 2, 'Destination', cell_format)
			# worksheet_hotel_summery.merge_range(14, 2,14, 3, 'Destination',cell_format)


			# worksheet_hotel_summery.merge_range('B14:C14', 'Hotel Name', merge_format)
			worksheet_hotel_summery.set_column(1, 1, 20)
			worksheet_hotel_summery.write(14, 3, 'Total Bill Amount by SAR', cell_format)
			worksheet_hotel_summery.merge_range(14, 4,14, 5, 'Total Bill Amount by SAR',cell_format)

			# worksheet_hotel_summery.merge_range('D14:E14', 'Merged Range', merge_format)
			# worksheet_hotel_summery.freeze_panes(14, 0, 1, 0)

			row = 14
			total_pkg_total = 0
			for x in hotel_summary_list:

				row += 1
				worksheet_hotel_summery.write(row, 1, x['hotel_name'])
				worksheet_hotel_summery.merge_range(row, 1,row, 3, x['hotel_name'])
				worksheet_hotel_summery.write(row, 2, x['pkg_total'])
				worksheet_hotel_summery.merge_range(row, 4,row, 5, x['pkg_total'])
				total_pkg_total += x['pkg_total']

			# worksheet_hotel_summery.set_row(12, 40)
			worksheet_hotel_summery.write(row, 1, 'Total', cell_format)
			worksheet_hotel_summery.merge_range(row, 1,row, 3, 'Total',cell_format)
			# worksheet_hotel_summery.set_column(1, 1, 20)
			worksheet_hotel_summery.write(row, 2, total_pkg_total, cell_format)
			worksheet_hotel_summery.merge_range(row, 4,row, 5, total_pkg_total,cell_format)
			####################################################################
			######################### Data for summery ENDS HERE #########################
			####################################################################

		##########################################################################
		####################### Data for Hotel Detailed Starts ########################
		######################################################################
		hotel_row = 2
		row = 3
		for x in hotel_main_list:
			# row += 2
			# hotel_row += 2
			# print("________________________-")
			worksheet_hotel_report = workbook .add_worksheet(x['hotel'])
			cell_format = workbook.add_format({'align': 'left', 'font_size': 20, 'underline': True})
			headibng_format = workbook.add_format({'align': 'left', 'font_size': 15})
			worksheet_hotel_report.set_row(0, 40)
			worksheet_hotel_report.write(0, 5, 'DMC Report', cell_format)
			date = 'From: '+str(form)+' TO: '+ str(to)
			worksheet_hotel_report.write(1, 5, date)
			worksheet_hotel_report.set_row(4, 40)
			worksheet_hotel_report.write(hotel_row,1, x['hotel'],headibng_format)
			# worksheet_hotel_report.write(hotel_row,2, x['destination'],headibng_format)
			worksheet_hotel_report.set_row(4, 40)
			detailed_formate = workbook.add_format({'align': 'centre', 'font_size': 12,'underline': True,'bold': True, 'fg_color': '#DAD7DD', 'text_wrap': True})
			worksheet_hotel_report.set_column(4, 40)
			worksheet_hotel_report.write(row, 0, 'Invoice No', detailed_formate)
			worksheet_hotel_report.write(row, 1, 'Branch', detailed_formate)
			worksheet_hotel_report.set_column(1, 1, 22)
			worksheet_hotel_report.write(row, 2, 'RQ No', detailed_formate)
			worksheet_hotel_report.set_column(2, 2, 22)
			worksheet_hotel_report.write(row, 3, 'Customer Name', detailed_formate)
			worksheet_hotel_report.set_column(3, 3, 22)
			worksheet_hotel_report.write(row, 4, 'Hotel Name', detailed_formate)

			worksheet_hotel_report.set_column(4, 4, 22)
			worksheet_hotel_report.write(row, 5, 'Room Type', detailed_formate)

			worksheet_hotel_report.set_column(5, 5, 22)
			worksheet_hotel_report.write(row, 6, 'No of Guest', detailed_formate)
			worksheet_hotel_report.set_column(6, 6, 22)


			worksheet_hotel_report.write(row, 7, 'Book Date', detailed_formate)
			worksheet_hotel_report.set_column(7, 7, 22)
			worksheet_hotel_report.write(row, 8, 'Arrival Date', detailed_formate)
			worksheet_hotel_report.set_column(8, 8, 22)


			worksheet_hotel_report.write(row, 9, 'Check In', detailed_formate)
			worksheet_hotel_report.set_column(9, 9, 22)
			worksheet_hotel_report.write(row, 10, 'Check Out', detailed_formate)
			worksheet_hotel_report.set_column(10, 10, 22)
			worksheet_hotel_report.write(row, 11, 'Total Nights', detailed_formate)
			worksheet_hotel_report.set_column(11, 11, 22)
			worksheet_hotel_report.write(row, 12, 'Amount FC', detailed_formate)
			worksheet_hotel_report.set_column(12, 12, 22)
			worksheet_hotel_report.write(row, 13, 'Currency', detailed_formate)
			worksheet_hotel_report.set_column(13, 13, 22)
			worksheet_hotel_report.write(row, 14, 'Total Bill Amount by SAR', detailed_formate)
			worksheet_hotel_report.set_column(14, 14, 22)
			worksheet_hotel_report.write(row, 15, 'Creation Date', detailed_formate)
			worksheet_hotel_report.set_column(15, 15, 22)
			# worksheet_hotel_report.set_column(13, 13, 22)
			worksheet_hotel_report.write(row, 16, 'Sales Person', detailed_formate)
			worksheet_hotel_report.set_column(17, 17, 22)
			worksheet_hotel_report.write(row, 17, 'Bill Status', detailed_formate)
			worksheet_hotel_report.freeze_panes(1, 0, 1, 0)
			# worksheet_hotel_report.freeze_panes(1, 0, 1, 0)
			line = row
			total_nights = 0
			total_amount_fc = 0
			toatal_pkage_amount = 0
			for data in x['main_list']:
				rooms = ''
				for data_room_type in data['room_type']:
					rooms += data_room_type

				customer_name_custom = ''
				for data_customers in data['customer_name']:
					# customer_name_custom = data_customers +'\n'+ customer_name_custom
					customer_name_custom += data_customers
				line += 1
				# print(row)                    
				# creation_date = datetime.datetime.strftime(data['creation_date'], "%Y-%m-%d")
				worksheet_hotel_report.write(line, 0, data['Invoice_no'])
				worksheet_hotel_report.write(line, 2, data['rq_number'])
				# if report_type == 'vendor':
				worksheet_hotel_report.write(line, 3, customer_name_custom)


				all_h_n = ""
				for h in data['Hotel_name']:
					all_h_n +='%s \n'%h


				if report_type == 'hotel':
					worksheet_hotel_report.write(line, 4, all_h_n)

				else:
					worksheet_hotel_report.write(line, 4, data['get_Hotel_name'])

				
				worksheet_hotel_report.write(line, 5,rooms )
				# if report_type == 'destination':
				#     worksheet_hotel_report.write(line, 2, data['Destination'])
				worksheet_hotel_report.write(line, 6, str(data['no_of_guest']))
				worksheet_hotel_report.write(line, 7, str(data['date_order']+timedelta(hours=5)))
				worksheet_hotel_report.write(line, 8, str(data['arrival_date']))

				worksheet_hotel_report.write(line, 9, str(data['check_in']))
				worksheet_hotel_report.write(line, 10, str(data['check_out']))


				worksheet_hotel_report.write(line, 11, data['nights'])
				worksheet_hotel_report.write_number(line, 12, float(data['amount_fc']))
				# worksheet_hotel_report.write(line, 5, data['amount_fc'])
				worksheet_hotel_report.write(line, 13, data['currency_id'])
				# worksheet_hotel_report.write(line, 7, data['toatal_pkage_amount'])
				worksheet_hotel_report.write_number(line, 14, float(data['toatal_pkage_amount']))
				worksheet_hotel_report.write(line,15, data['creation_date'])
				worksheet_hotel_report.write(line, 16, data['sale_person'])
				worksheet_hotel_report.write(line, 17, data['status'])
				total_nights += data['nights']
				total_amount_fc += data['amount_fc']
				toatal_pkage_amount += data['toatal_pkage_amount']
			line += 1
			worksheet_hotel_report.set_column(line, 40)
			worksheet_hotel_report.write(line, 0, 'Total', detailed_formate)
			worksheet_hotel_report.set_column(1, 1, 22)
			worksheet_hotel_report.write(line, 1, '-', detailed_formate)
			worksheet_hotel_report.set_column(2, 2, 22)
			worksheet_hotel_report.write(line, 2, '-', detailed_formate)
			worksheet_hotel_report.set_column(3, 3, 22)
			worksheet_hotel_report.write(line, 3, '-', detailed_formate)
			worksheet_hotel_report.set_column(4, 4, 22)
			worksheet_hotel_report.write(line, 4, '-', detailed_formate)
			worksheet_hotel_report.set_column(5, 5, 22)
			worksheet_hotel_report.write(line, 5, '-', detailed_formate)
			worksheet_hotel_report.set_column(6, 6, 22)
			worksheet_hotel_report.write(line, 6, '-', detailed_formate)
			worksheet_hotel_report.set_column(7, 7, 22)
			worksheet_hotel_report.write(line, 7, '-', detailed_formate)
			worksheet_hotel_report.set_column(8, 8, 22)
			worksheet_hotel_report.write(line, 8, '-', detailed_formate)
			worksheet_hotel_report.set_column(9, 9, 22)
			worksheet_hotel_report.write(line, 9, '-', detailed_formate)
			worksheet_hotel_report.set_column(10, 10, 22)
			worksheet_hotel_report.write(line, 10, '-', detailed_formate)
			worksheet_hotel_report.set_column(11, 11, 22)
			worksheet_hotel_report.write(line, 11, total_nights, detailed_formate)
			worksheet_hotel_report.set_column(12, 12, 22)
			worksheet_hotel_report.write(line, 12, total_amount_fc, detailed_formate)
			worksheet_hotel_report.set_column(13, 13, 22)
			worksheet_hotel_report.write(line, 13, '-', detailed_formate)
			worksheet_hotel_report.set_column(14, 14, 22)
			worksheet_hotel_report.write(line, 14, toatal_pkage_amount, detailed_formate)
			worksheet_hotel_report.set_column(15, 15, 22)
			worksheet_hotel_report.write(line, 15, '-' , detailed_formate)
			worksheet_hotel_report.set_column(16, 16, 22)
			worksheet_hotel_report.write(line, 16, '-', detailed_formate)
			worksheet_hotel_report.set_column(17, 17, 22)
			worksheet_hotel_report.write(line, 17, '-', detailed_formate)