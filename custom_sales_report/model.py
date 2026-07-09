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
from odoo.exceptions import ValidationError, UserError
import datetime
from datetime import date
from datetime import date, timedelta
import datetime
from dateutil.relativedelta import *
import math
from PIL import Image, ImageDraw
import xlsxwriter



class custom_sales_report(models.AbstractModel):
	_name = 'report.custom_sales_report.custom_sales_report'
	_description = 'Custom PDF Sale Report'

	@api.model
	def _get_report_values(self, docids, data=None):
		record_wizard = self.env['custom.sales.report'].browse(self.env.context.get('active_ids'))
		form = record_wizard.form
		to = record_wizard.to
		company = record_wizard.company_id
		is_com = record_wizard.is_com
		partner_id = record_wizard.partner_id

		hotel = record_wizard.hotel

		country_id = record_wizard.country_id
		booking_type = record_wizard.booking_type
		product_id = record_wizard.product_id

		if partner_id:
			partner = []
			for x in partner_id:
				partner.append(x)
		else:
			partner = self.env['hr.employee'].search([])


		main_list_type = []
		for product in product_id:

			emp_main_list = []
			# print(product.name)
			for x in partner:
				# print(x.name)

				hotel_search = ('id','!=',False)
				if product.prod_serv_typecategory == 'hotel':
					if hotel:
						hotel_search = ('hotel_id','=',hotel.id)

				if is_com == 'is_c':
					commissioned = ('itinarnay_return.commissioned','=',True)
				elif is_com == 'is_not_c':
					commissioned = ('itinarnay_return.commissioned','=',False)
				else:
					commissioned = ('id','!=',False)

				if booking_type == 'book_date':
					booking_type_search_from = ('itinarnay_return.date_order','>=',form)
					booking_type_search_to = ('itinarnay_return.date_order','<=',to)
				else:
					booking_type_search_from = ('itinarnay_return.arrival_date','>=',form)
					booking_type_search_to = ('itinarnay_return.arrival_date','<=',to)

				record = self.env['all.services'].search([('product_id','=',product.id),('itinarnay_return.user_id','=',x.user_id.id),('itinarnay_return.stages','=','validate'),commissioned,booking_type_search_from,booking_type_search_to,hotel_search])

				main_list = []
				serial_total = 0
				if record:
					for rec in record:
						destination_list = []
						if country_id:
							if country_id.id in rec.itinarnay_return.destination.ids:
								serial_total += 1
								for t in rec.itinarnay_return.destination:
									if t.id == country_id.id:
										destination_list.append(t.name)
								
								room_type_list = []
								for t in rec.room_type:
									room_type_list.append(t.name)
								main_list.append({
									'id':rec.id,
									'product_id':product.name,
									'rq_number':rec.itinarnay_return.name,
									'sale_person':x.name,
									'hotel_name':rec.hotel_id.name,
									'date_order':rec.itinarnay_return.date_order,
									'arrival_date':rec.itinarnay_return.arrival_date,
									'departure_date':rec.itinarnay_return.departure_date,
									'date_from':rec.date_from,
									'date_to':rec.date_to,
									'destination':destination_list,
									'no_of_nights':rec.nights,
									'flight_name':rec.airline.name,
									'guest_name':rec.itinarnay_return.partner_id.name,
									'net':rec.price,
									'net_fc':rec.amnt_fc,
									'commission':rec.commission,
									'total':rec.total,
									'room_type':room_type_list,
									# 'room_type':inv.room_type.ids,
									})
						else:

							for t in rec.itinarnay_return.destination:
								destination_list.append(t.name)
							serial_total += 1
							room_type_list = []
							for t in rec.room_type:
								room_type_list.append(t.name)
							main_list.append({
								'id':rec.id,
								'product_id':product.name,
								'rq_number':rec.itinarnay_return.name,
								'sale_person':x.name,
								'hotel_name':rec.hotel_id.name,
								'date_from':rec.date_from,
								'date_to':rec.date_to,
								'date_order':rec.itinarnay_return.date_order,
								'arrival_date':rec.itinarnay_return.arrival_date,
								'departure_date':rec.itinarnay_return.departure_date,
								'flight_name':rec.airline.name,
								'destination':destination_list,
								'no_of_nights':rec.nights,
								'guest_name':rec.itinarnay_return.partner_id.name,
								'net':rec.price,
								'net_fc':rec.amnt_fc,
								'commission':rec.commission,
								'total':rec.total,
								'room_type':room_type_list,
								'country_id':rec.itinarnay_return.destination,
								# 'room_type':inv.room_type.ids,
								})
				if main_list:
					emp_main_list.append({
						'employee':x.name,
						'serial_total':serial_total,
						'main_list':main_list,
						})

			main_list_type.append({
				'type':product.name,
				'emp_main_list':emp_main_list,
				})
		return {
			'doc_ids': docids,
			'doc_model':'all.services',
			'form': form,
			'to': to,
			'company': company,
			'main_list_type': main_list_type,
		}
class custom_sales_report_xlsx(models.AbstractModel):
	_name = 'report.custom_sales_report.custom_sales_report_xlsx'
	_inherit = 'report.report_xlsx.abstract'
	_description="Custom Sales Report"

	def generate_xlsx_report(self, workbook, data, wizard_obj):

		record_wizard = self.env[data['context']['active_model']].browse(self.env.context.get('active_id'))
		form = record_wizard.form
		to = record_wizard.to
		company = record_wizard.company_id
		is_com = record_wizard.is_com
		partner_id = record_wizard.partner_id
		hotel = record_wizard.hotel
		country_id = record_wizard.country_id
		booking_type = record_wizard.booking_type
		product_id = record_wizard.product_id
		if partner_id:
			partner = []
			for x in partner_id:
				partner.append(x)
		else:
			partner = self.env['hr.employee'].search([])


		main_list_type = []
		for product in product_id:

			emp_main_list = []
			for x in partner:
				hotel_search = ('id','!=',False)
				if product.prod_serv_typecategory == 'hotel':
					if hotel:
						hotel_search = ('hotel_id','=',hotel.id)

				if is_com == 'is_c':
					commissioned = ('itinarnay_return.commissioned','=',True)
				elif is_com == 'is_not_c':
					commissioned = ('itinarnay_return.commissioned','=',False)
				else:
					commissioned = ('id','!=',False)

				if booking_type == 'book_date':
					booking_type_search_from = ('itinarnay_return.date_order','>=',form)
					booking_type_search_to = ('itinarnay_return.date_order','<=',to)
				else:
					booking_type_search_from = ('itinarnay_return.arrival_date','>=',form)
					booking_type_search_to = ('itinarnay_return.arrival_date','<=',to)

				record = self.env['all.services'].search([('product_id','=',product.id),('itinarnay_return.user_id','=',x.user_id.id),('itinarnay_return.stages','=','validate'),commissioned,booking_type_search_from,booking_type_search_to,hotel_search])

				main_list = []
				serial_total = 0
				if record:
					for rec in record:
						destination_list = []
						if country_id:
							if country_id.id in rec.itinarnay_return.destination.ids:
								serial_total += 1
								for t in rec.itinarnay_return.destination:
									if t.id == country_id.id:
										destination_list.append(t.name)
								
								room_type_list = []
								for t in rec.room_type:
									room_type_list.append(t.name)
								main_list.append({
									'id':rec.id,
									'product_id':product.name,
									'rq_number':rec.itinarnay_return.name,
									'sale_person':x.name,
									'hotel_name':rec.hotel_id.name,
									'date_order':rec.itinarnay_return.date_order,
									'arrival_date':rec.itinarnay_return.arrival_date,
									'departure_date':rec.itinarnay_return.departure_date,
									'destination':destination_list,
									'no_of_nights':rec.nights,
									'flight_name':rec.airline.name,
									'guest_name':rec.itinarnay_return.partner_id.name,
									'net':rec.price,
									'net_fc':rec.amnt_fc,
									'commission':rec.commission,
									'total':rec.total,
									'room_type':room_type_list,
									# 'room_type':inv.room_type.ids,
									})
						else:

							for t in rec.itinarnay_return.destination:
								destination_list.append(t.name)
							serial_total += 1
							room_type_list = []
							for t in rec.room_type:
								room_type_list.append(t.name)
							main_list.append({
								'id':rec.id,
								'product_id':product.name,
								'rq_number':rec.itinarnay_return.name,
								'sale_person':x.name,
								'hotel_name':rec.hotel_id.name,
								'date_order':rec.itinarnay_return.date_order,
								'arrival_date':rec.itinarnay_return.arrival_date,
								'departure_date':rec.itinarnay_return.departure_date,
								'flight_name':rec.airline.name,
								'destination':destination_list,
								'no_of_nights':rec.nights,
								'guest_name':rec.itinarnay_return.partner_id.name,
								'net':rec.price,
								'net_fc':rec.amnt_fc,
								'commission':rec.commission,
								'total':rec.total,
								'room_type':room_type_list,
								'country_id':rec.itinarnay_return.destination,
								# 'room_type':inv.room_type.ids,
								})
				if main_list:
					emp_main_list.append({
						'employee':x.name,
						'serial_total':serial_total,
						'main_list':main_list,
						})

			main_list_type.append({
				'type':product.name,
				'emp_main_list':emp_main_list,
				})


		row = 9
		employee_sales = workbook.add_worksheet()
			# for data in main_list:
				# employee_sales = workbook.add_worksheet(emp['employee'])
				# row += 1
				# tot_row += 1
				# tot_salary += emp['salary']

				########################################################################
				#######################################################################
				#####################creating styles and data for summery ##########
				######################################################################
				#######################################################################

		h4_bold = workbook.add_format({'bold': True, 'align': 'left', 'font_size': 10})
		employee_sales.merge_range(1, 1,1, 5, company.name, h4_bold)
		employee_sales.merge_range(2, 1,2, 5, company.street, h4_bold)
		employee_sales.merge_range(3, 1,3, 5, company.street2, h4_bold)
		employee_sales.merge_range(4, 1,4, 5, company.city, h4_bold)
		employee_sales.merge_range(5, 1,5, 5, company.country_id.name, h4_bold)
		employee_sales.write(6, 1, 'CR No:', h4_bold)
		employee_sales.merge_range(6, 2,6, 5, company.company_registry, h4_bold)
		employee_sales.write(7, 1, 'Ph:', h4_bold)
		employee_sales.merge_range(7, 2,7, 5, company.phone, h4_bold)
		employee_sales.write(8, 1,'Email:', h4_bold)
		employee_sales.merge_range(8, 2, 8, 5, company.email, h4_bold)
		employee_sales.write(9, 1, 'Vat', h4_bold)
		employee_sales.merge_range(9, 2,9, 5, company.vat, h4_bold)
		cell_format = workbook.add_format({'align': 'centre', 'font_size': 15, 'underline': True})
		employee_sales.set_row(10, 25)
		date_format = workbook.add_format({'align': 'centre', 'font_size': 13, 'underline': True})
		date = 'From: '+str(form)+' TO: '+ str(to)
		employee_sales.merge_range(11, 1,11, 14, 'Sales Report',cell_format)
		employee_sales.write(12, 1, date,date_format)
		employee_sales.merge_range(12, 1,12, 14, date,date_format)

		# ##########################################################################
		# ####################### Data for sale Starts ########################
		# ######################################################################


		value_style = workbook.add_format({'align': 'left', 'font_size': 10})
		heading_row = 14 
		for data in main_list_type:
			heading_row += 1 
			for a in data['emp_main_list']:
				employee_sales.merge_range(heading_row, 1,heading_row, 2, 'No Of Booking', h4_bold)
				employee_sales.merge_range(heading_row, 3,heading_row, 6, a['serial_total'], value_style)
				heading_row += 1
				employee_sales.merge_range(heading_row, 1,heading_row, 2, 'Salesperson', h4_bold)
				employee_sales.merge_range(heading_row, 3,heading_row, 6, a['employee'], value_style)
				heading_row += 1
				employee_sales.merge_range(heading_row, 1,heading_row, 14, data['type'], cell_format)

				table_head = workbook.add_format({'align': 'centre', 'font_size': 10,'bold': True, 'fg_color': '#DAD7DD', 'text_wrap': True,'border':1})

				employee_sales.set_column(0, 0, 15)
				heading_row += 2
				cl = 1
				cl2 = 2
				employee_sales.merge_range(heading_row, cl,heading_row, cl2, 'RQ No', table_head)
				cl += 2
				cl2 += 2
				employee_sales.merge_range(heading_row, cl,heading_row, cl2, 'Branch', table_head)
				cl += 2
				cl2 += 2
				employee_sales.merge_range(heading_row, cl,heading_row, cl2, 'Sales Person', table_head)
				cl += 2
				cl2 += 2
				if data['type'] == 'Hotel':
					employee_sales.merge_range(heading_row, cl,heading_row, cl2, 'Hotel Name', table_head)
					cl += 2
					cl2 += 2
				if data['type'] == 'Flight':
					employee_sales.merge_range(heading_row, cl,heading_row, cl2, 'Flight Name', table_head)
					cl += 2
					cl2 += 2
				employee_sales.merge_range(heading_row, cl,heading_row, cl2, 'Destination', table_head)
				cl += 2
				cl2 += 2
				if data['type'] == 'Hotel':
					employee_sales.merge_range(heading_row, cl,heading_row, cl2, 'Villa Type', table_head)
					cl += 2
					cl2 += 2
				employee_sales.merge_range(heading_row, cl,heading_row, cl2, 'Book Date', table_head)
				cl += 2
				cl2 += 2
				employee_sales.merge_range(heading_row, cl,heading_row, cl2, 'Arrival Date', table_head)
				cl += 2
				cl2 += 2
				employee_sales.merge_range(heading_row, cl,heading_row, cl2, 'Departure Date', table_head)
				cl += 2
				cl2 += 2
				if data['type'] == 'Hotel':
					employee_sales.merge_range(heading_row, cl,heading_row, cl2, 'Number of Nights', table_head)
					cl += 2
					cl2 += 2
				employee_sales.merge_range(heading_row, cl,heading_row, cl2, 'Guest name', table_head)
				cl += 2
				cl2 += 2
				employee_sales.merge_range(heading_row, cl,heading_row, cl2, 'Net', table_head)
				cl += 2
				cl2 += 2
				employee_sales.merge_range(heading_row, cl,heading_row, cl2, 'Net Amount FC', table_head)
				cl += 2
				cl2 += 2
				employee_sales.merge_range(heading_row, cl,heading_row, cl2, 'Commission', table_head)
				cl += 2
				cl2 += 2
				employee_sales.merge_range(heading_row, cl,heading_row, cl2, 'Total', table_head)
				table_td = workbook.add_format({'align': 'left', 'font_size': 10, 'text_wrap': True,'border':1})
				row = heading_row
				employee_sales.set_row(row, 25)
		
				for z in a['main_list']:
					
					row += 1
					cd1 = 1
					cd2 = 2
					employee_sales.merge_range(row, cd1,row, cd2, z['rq_number'],table_td)
					cd1 += 2
					cd2 += 2
					cd1 += 2
					cd2 += 2
					employee_sales.merge_range(row, cd1,row, cd2, z['sale_person'],table_td)
					cd1 += 2
					cd2 += 2
					if data['type'] == 'Hotel':
						employee_sales.merge_range(row, cd1,row,cd2, z['hotel_name'],table_td)
						cd1 += 2
						cd2 += 2
					if data['type'] == 'Flight':
						employee_sales.merge_range(row, cd1,row,cd2, z['flight_name'],table_td)
						cd1 += 2
						cd2 += 2
					destination = ''
					for x in z['destination']:
						if destination:
							destination = x +',' + destination
						if not destination:
								destination = x

					room_types = ''
					for x in z['room_type']:
						if room_types:
							room_types = x +',' + room_types
						if not room_types:
							room_types = x

					employee_sales.merge_range(row, cd1,row, cd2, destination,table_td)
					cd1 += 2
					cd2 += 2
					if data['type'] == 'Hotel':
						employee_sales.merge_range(row, cd1,row, cd2, room_types,table_td)
						cd1 += 2
						cd2 += 2
					employee_sales.merge_range(row, cd1,row, cd2, str(z['date_order']+timedelta(hours=5)),table_td)
					cd1 += 2
					cd2 += 2
					employee_sales.merge_range(row, cd1,row, cd2, str(z['arrival_date']),table_td)
					cd1 += 2
					cd2 += 2
					employee_sales.merge_range(row, cd1,row, cd2, str(z['departure_date']),table_td)
					cd1 += 2
					cd2 += 2
					if data['type'] == 'Hotel':
						employee_sales.merge_range(row, cd1,row, cd2, z['no_of_nights'],table_td)
						cd1 += 2
						cd2 += 2
					employee_sales.merge_range(row, cd1,row, cd2, z['guest_name'],table_td)
					cd1 += 2
					cd2 += 2
					employee_sales.merge_range(row, cd1,row, cd2, float(z['net']),table_td)
					cd1 += 2
					cd2 += 2
					employee_sales.merge_range(row, cd1,row, cd2, float(z['net_fc']),table_td)
					cd1 += 2
					cd2 += 2
					employee_sales.merge_range(row, cd1,row, cd2, float(z['commission']),table_td)
					cd1 += 2
					cd2 += 2
					employee_sales.merge_range(row, cd1,row, cd2, float(z['total']),table_td)
				heading_row = row
				heading_row += 2

