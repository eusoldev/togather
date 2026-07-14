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
import json
import urllib.parse
import urllib.request
from PIL import Image, ImageDraw
import xlsxwriter




class check_arrival_date_report(models.AbstractModel):
	_name = 'report.check_arrival_date_report.check_arrival_date_report'
	_description = 'Arriavl And Departure Report'

	@api.model
	def _get_report_values(self, docids, data=None):
		
		record_wizard = self.env['check.date.report'].browse(self.env.context.get('active_ids'))
		company = record_wizard.company_id or self.env.company
		

		form = record_wizard.form
		to = record_wizard.to

		record = self.env['all.services'].search([('hotel_return.arrival_date','>=',form),('hotel_return.departure_date','<=',to),('hotel_return.stages','=','validate')])

		main_list = []
		for x in record:
			room_type_list = []
			for t in x.room_type:
				room_type_list.append(t.name)
			meal_list = []
			for z in x.hotel_meal_plan:
				meal_list.append(z.name)
			transfer_list = []
			for y in x.transfer:
				transfer_list.append(y.name)
			main_list.append({
				'guest':x.hotel_return.partner_id.name,
				'hotel':x.hotel_id.name,
				'sub_agent':x.hotel_return.agent.name,

				'name':x.hotel_return.name,
				'arrival_date':x.hotel_return.arrival_date,
				'arrival_flight':x.hotel_return.hotel_arrival.name,
				'departure_date':x.hotel_return.departure_date,
				'departure_flight':x.hotel_return.hotel_return.name,
				'confirmation_no':x.confirmation_no,
				'contract_no':x.hotel_return.partner_id.mobile,
				# 'contract_no':x.confirmation_no,
				'phone_no':x.hotel_return.partner_id.phone,
				'room_qty':x.room_qty,
				'room_type': room_type_list,
				'meal_plan':meal_list,
				'transfer_type':transfer_list,
				# 'room_type':x.room_type.name,
				# 'meal_plan':x.hotel_meal_plan.name,
				# 'transfer_type':x.transfer.name,
				'special_remarks':x.special_remarks,
				'applied_offer':x.offered_applied,
				'fc_amount':x.amnt_fc,
				})
		arrival = self.env['all.services'].search([('hotel_return.arrival_date','>=',form),('hotel_return.arrival_date','<=',to),('hotel_return.stages','=','validate')])
		arrival_dates = []
		for x in arrival:
			room_type_list = []
			for t in x.room_type:
				room_type_list.append(t.name)
			meal_list = []
			for z in x.hotel_meal_plan:
				meal_list.append(z.name)
			transfer_list = []
			for y in x.transfer:
				transfer_list.append(y.name)
			arrival_dates.append({
				'guest':x.hotel_return.partner_id.name,
				'name':x.hotel_return.name,
				'hotel':x.hotel_id.name,
				'sub_agent':x.hotel_return.agent.name,
				'arrival_date':x.hotel_return.arrival_date,
				'arrival_flight':x.hotel_return.hotel_arrival.name,
				'departure_date':x.hotel_return.departure_date,
				'departure_flight':x.hotel_return.hotel_return.name,
				'confirmation_no':x.confirmation_no,
				'contract_no':x.hotel_return.partner_id.mobile,
				'phone_no':x.hotel_return.partner_id.phone,
				'room_qty':x.room_qty,
				'room_type': room_type_list,
				'meal_plan':meal_list,
				'transfer_type':transfer_list,
				# 'room_type':x.room_type.name,
				# 'meal_plan':x.hotel_meal_plan.name,
				# 'transfer_type':x.transfer.name,
				'special_remarks':x.special_remarks,
				'applied_offer':x.offered_applied,
				'fc_amount':x.amnt_fc,
				})
		departure = self.env['all.services'].search([('hotel_return.departure_date','>=',form),('hotel_return.departure_date','<=',to),('hotel_return.stages','=','validate')])
		departure_dates = []
		for x in departure:
			room_type_list = []
			for t in x.room_type:
				room_type_list.append(t.name)
			meal_list = []
			for z in x.hotel_meal_plan:
				meal_list.append(z.name)
			transfer_list = []
			for y in x.transfer:
				transfer_list.append(y.name)
			departure_dates.append({
				'guest':x.hotel_return.partner_id.name,
				'name':x.hotel_return.name,
				'hotel':x.hotel_id.name,
				'sub_agent':x.hotel_return.agent.name,
				'arrival_date':x.hotel_return.arrival_date,
				'arrival_flight':x.hotel_return.hotel_arrival.name,
				'departure_date':x.hotel_return.departure_date,
				'departure_flight':x.hotel_return.hotel_return.name,
				'confirmation_no':x.confirmation_no,
				'contract_no':x.hotel_return.partner_id.mobile,
				'phone_no':x.hotel_return.partner_id.phone,
				'room_qty':x.room_qty,
				'room_type': room_type_list,
				'meal_plan':meal_list,
				'transfer_type':transfer_list,
				# 'room_type':x.room_type.name,
				# 'meal_plan':x.hotel_meal_plan.name,
				# 'transfer_type':x.transfer.name,
				'special_remarks':x.special_remarks,
				'applied_offer':x.offered_applied,
				'fc_amount':x.amnt_fc,
				})


		return {
			'doc_ids': docids,
			'doc_model':'all.services',
			'form': form,
			'to': to,
			'company': company,
			'main_list':main_list,
			'arrival_dates':arrival_dates,
			'departure_dates':departure_dates,
		}





class check_arrival_date_report_xlsx(models.AbstractModel):
	_name = 'report.check_arrival_date_report.check_arrival_date_report_xlsx'
	_inherit = 'report.report_xlsx.abstract'
	_description="Check Arrival Date Report"





	def generate_xlsx_report(self, workbook, data, wizard_obj):
		# record_wizard = self.env[data['context']['active_model']].browse(self.env.context.get('active_id'))
		record_wizard = self.env['check.date.report'].browse(self.env.context.get('active_ids'))

		form = record_wizard.form
		to = record_wizard.to


		record = self.env['all.services'].search([('hotel_return.arrival_date','>=',form),('hotel_return.departure_date','<=',to),('hotel_return.stages','=','validate')])
		main_list = []
		for x in record:
			room_type_list = ''
			for t in x.room_type:
				room_type_list = str(t.name) +' , '+ room_type_list 
			meal_list = ''
			for z in x.hotel_meal_plan:
				meal_list = str(z.name) + ', '+ meal_list
			transfer_list = ''
			for y in x.transfer:
				transfer_list = str(y.name) + ', ' + transfer_list

			main_list.append({
				'guest':x.hotel_return.partner_id.name,
				'hotel':x.hotel_id.name,
				'sub_agent':x.hotel_return.agent.name,
				'name':x.hotel_return.name,
				'arrival_date':x.hotel_return.arrival_date,
				'arrival_flight':x.hotel_return.hotel_arrival.name,
				'departure_date':x.hotel_return.departure_date,
				'departure_flight':x.hotel_return.hotel_return.name,
				'confirmation_no':x.confirmation_no,
				'contract_no':x.hotel_return.partner_id.mobile,
				'phone_no':x.hotel_return.partner_id.mobile,
				'room_qty':x.room_qty,
				'room_type': room_type_list,
				'meal_plan':meal_list,
				'transfer_type':transfer_list,
				# 'room_type':x.room_type.name,
				# 'meal_plan':x.hotel_meal_plan.name,
				# 'transfer_type':x.transfer.name,
				'special_remarks':x.special_remarks,
				'applied_offer':x.offered_applied,
				'fc_amount':x.amnt_fc,
				})

		arrival = self.env['all.services'].search([('hotel_return.arrival_date','>=',form),('hotel_return.arrival_date','<=',to),('hotel_return.stages','=','validate')])
		arrival_dates = []
		for x in arrival:
			room_type_list = ''
			for t in x.room_type:
				room_type_list = str(t.name) +' , '+ room_type_list 
			meal_list = ''
			for z in x.hotel_meal_plan:
				meal_list = str(z.name) + ', '+ meal_list
			transfer_list = ''
			for y in x.transfer:
				transfer_list = str(y.name) + ', ' + transfer_list

			arrival_dates.append({
				'guest':x.hotel_return.partner_id.name,
				'hotel':x.hotel_id.name,
				'sub_agent':x.hotel_return.agent.name,
				'name':x.hotel_return.name,
				'arrival_date':x.hotel_return.arrival_date,
				'arrival_flight':x.hotel_return.hotel_arrival.name,
				'departure_date':x.hotel_return.departure_date,
				'departure_flight':x.hotel_return.hotel_return.name,
				'confirmation_no':x.confirmation_no,
				'contract_no':x.hotel_return.partner_id.mobile,
				'phone_no':x.hotel_return.partner_id.mobile,
				'room_qty':x.room_qty,
				'room_type': room_type_list,
				'meal_plan':meal_list,
				'transfer_type':transfer_list,
				# 'room_type':x.room_type.name,
				# 'meal_plan':x.hotel_meal_plan.name,
				# 'transfer_type':x.transfer.name,
				'special_remarks':x.special_remarks,
				'applied_offer':x.offered_applied,
				'fc_amount':x.amnt_fc,
				})
		  

		departure = self.env['all.services'].search([('hotel_return.departure_date','>=',form),('hotel_return.departure_date','<=',to),('hotel_return.stages','=','validate')])
		departure_dates = []
		for x in departure:
			room_type_list = ''
			for t in x.room_type:
				room_type_list = str(t.name) +' , '+ room_type_list 
			meal_list = ''
			for z in x.hotel_meal_plan:
				meal_list = str(z.name) + ', '+ meal_list
			transfer_list = ''
			for y in x.transfer:
				transfer_list = str(y.name) + ', ' + transfer_list

			departure_dates.append({
				'guest':x.hotel_return.partner_id.name,
				'name':x.hotel_return.name,
				'hotel':x.hotel_id.name,
				'sub_agent':x.hotel_return.agent.name,
				'arrival_date':x.hotel_return.arrival_date,
				'arrival_flight':x.hotel_return.hotel_arrival.name,
				'departure_date':x.hotel_return.departure_date,
				'departure_flight':x.hotel_return.hotel_return.name,
				'confirmation_no':x.confirmation_no,
				'contract_no':x.hotel_return.partner_id.mobile,
				'phone_no':x.hotel_return.partner_id.mobile,
				'room_qty':x.room_qty,
				'room_type': room_type_list,
				'meal_plan':meal_list,
				'transfer_type':transfer_list,
				# 'room_type':x.room_type.name,
				# 'meal_plan':x.hotel_meal_plan.name,
				# 'transfer_type':x.transfer.name,
				'special_remarks':x.special_remarks,
				'applied_offer':x.offered_applied,
				'fc_amount':x.amnt_fc,
				})
			
		##########################################################################
		####################### Data for Sub agent Detailed Starts ########################
		######################################################################
		# this method is used to create worksheet
		worksheet_agent_report = workbook.add_worksheet('Arrival And Departure Date')
		worksheet_arrival_report = workbook.add_worksheet('Arrival Date Report')
		worksheet_departure_report = workbook.add_worksheet('Departure Date Report')
		# worksheet_agent_report = workbook .add_worksheet(x['agent'])
		if main_list:
			cell_format = workbook.add_format({'bold': 1,'align': 'left', 'font_size':12, 'underline': True})
			headibng_format = workbook.add_format({'align': 'left', 'font_size': 15})
			worksheet_agent_report.set_row(0, 40)
			worksheet_agent_report.write(0, 5, 'Arrival And Departure Date', cell_format)
			date = 'From: '+str(form)+' TO: '+ str(to)
			worksheet_agent_report.write(1, 5, date)
			worksheet_agent_report.set_row(4, 40)
			# worksheet_agent_report.write(hotel_row,1, x['agent'],headibng_format)
			worksheet_agent_report.set_row(4, 40)
			detailed_formate = workbook.add_format({'align': 'centre', 'font_size': 12,'bold': True, 'fg_color': '#DAD7DD', 'text_wrap': True})
			worksheet_agent_report.set_column(4, 40)
			# worksheet_agent_report.set_column(0, 0,20)
			worksheet_agent_report.write(3, 0, 'Guest Name', detailed_formate)
			worksheet_agent_report.set_column(1, 1, 22)
			worksheet_agent_report.write(3, 1, 'Branch', detailed_formate)
			worksheet_agent_report.set_column(2, 2, 22)
			worksheet_agent_report.write(3, 2, 'Reservations No', detailed_formate)
			worksheet_agent_report.set_column(3, 3, 22)
			worksheet_agent_report.write(3, 3, 'Hotel Name', detailed_formate)
			worksheet_agent_report.set_column(4, 4, 22)
			worksheet_agent_report.write(3, 4, 'Sub Agent', detailed_formate)
			worksheet_agent_report.set_column(5, 5, 22)
			worksheet_agent_report.write(3, 5, 'Contact Number', detailed_formate)
			worksheet_agent_report.set_column(6, 6, 22)
			worksheet_agent_report.write(3, 6, 'Arrival Date', detailed_formate)
			worksheet_agent_report.set_column(7, 7, 22)
			worksheet_agent_report.write(3, 7, 'Arrival Flight', detailed_formate)
			worksheet_agent_report.set_column(8, 8, 22)
			worksheet_agent_report.write(3, 8, 'Departure Date', detailed_formate)
			worksheet_agent_report.set_column(9, 9, 22)
			worksheet_agent_report.write(3, 9, 'Departure Flight', detailed_formate)
			worksheet_agent_report.set_column(10, 10, 22)
			worksheet_agent_report.write(3, 10, 'Confirmation Number', detailed_formate)
			worksheet_agent_report.set_column(11, 11, 22)
			worksheet_agent_report.write(3, 11, 'Room Quantity', detailed_formate)
			worksheet_agent_report.set_column(12, 12, 22)
			worksheet_agent_report.write(3, 12, 'Room Type', detailed_formate)
			worksheet_agent_report.set_column(13, 13, 22)
			worksheet_agent_report.write(3, 13, 'Meal Plan', detailed_formate)
			worksheet_agent_report.set_column(14, 14, 22)
			worksheet_agent_report.write(3, 14, 'Transfer Type', detailed_formate)
			worksheet_agent_report.set_column(15 ,15, 22)
			worksheet_agent_report.write(3, 15, 'Special Remarks', detailed_formate)
			worksheet_agent_report.set_column(16, 16, 22)
			worksheet_agent_report.write(3, 16, 'Applied Offer', detailed_formate)
			worksheet_agent_report.set_column(17, 17, 22)
			worksheet_agent_report.write(3, 17, 'Net Amount FC', detailed_formate)
			worksheet_agent_report.freeze_panes(1, 0, 1, 0)
			line =4
			for data in main_list: 
				line += 1
				# print(row)
				worksheet_agent_report.write(line, 0, data['guest'])
				worksheet_agent_report.write(line, 2, data['name'])
				worksheet_agent_report.write(line, 3, data['hotel'])

			

				worksheet_agent_report.write(line, 4, data['sub_agent'])
			   


				worksheet_agent_report.write(line, 5, data['contract_no'])
				worksheet_agent_report.write(line, 6, str(data['arrival_date']))
				worksheet_agent_report.write(line, 7, str(data['arrival_flight']))
				worksheet_agent_report.write(line, 8, str(data['departure_date']))
				worksheet_agent_report.write(line, 9, data['departure_flight'])
				worksheet_agent_report.write(line, 10, data['confirmation_no'])
				worksheet_agent_report.write(line, 11, data['room_qty'])
				worksheet_agent_report.write(line, 12, data['room_type'])
				worksheet_agent_report.write(line, 13, data['meal_plan'])
				worksheet_agent_report.write(line, 14, data['transfer_type'])
				worksheet_agent_report.write(line, 15, data['special_remarks'])
				worksheet_agent_report.write(line, 16, data['applied_offer'])
				worksheet_agent_report.write(line, 17, data['fc_amount'])

		if arrival_dates:

			cell_format = workbook.add_format({'bold': 1,'align': 'left', 'font_size':12, 'underline': True})
			headibng_format = workbook.add_format({'align': 'left', 'font_size': 15})
			worksheet_arrival_report.set_row(0, 40)
			worksheet_arrival_report.write(0, 5, 'Arrival Date Report', cell_format)
			date = 'From: '+str(form)+' TO: '+ str(to)
			worksheet_arrival_report.write(1, 5, date)
			worksheet_arrival_report.set_row(4, 40)
			# worksheet_arrival_report.write(hotel_row,1, x['agent'],headibng_format)
			worksheet_arrival_report.set_row(4, 40)
			detailed_formate = workbook.add_format({'align': 'centre', 'font_size': 12,'bold': True, 'fg_color': '#DAD7DD', 'text_wrap': True})
			worksheet_arrival_report.set_column(4, 40)
			worksheet_arrival_report.set_column(0, 0,22)
			worksheet_arrival_report.write(3, 0, 'Guest Name', detailed_formate)
			worksheet_arrival_report.set_column(1, 1, 22)
			worksheet_arrival_report.write(3, 1, 'Branch', detailed_formate)
			worksheet_arrival_report.set_column(2, 2, 22)
			worksheet_arrival_report.write(3, 2, 'Reservations No', detailed_formate)
			worksheet_arrival_report.set_column(3, 3, 22)
			worksheet_arrival_report.write(3, 3, 'Hotel Name', detailed_formate)
			worksheet_arrival_report.set_column(4, 4, 22)
			worksheet_arrival_report.write(3, 4, 'Sub Agent', detailed_formate)
			worksheet_arrival_report.set_column(5, 5, 22)
			worksheet_arrival_report.write(3, 5, 'Contact Number', detailed_formate)
			worksheet_arrival_report.set_column(6, 6, 22)
			worksheet_arrival_report.write(3, 6, 'Arrival Date', detailed_formate)
			worksheet_arrival_report.set_column(7, 7, 22)
			worksheet_arrival_report.write(3, 7, 'Arrival Flight', detailed_formate)
			# worksheet_arrival_report.set_column(4, 4, 22)
			# worksheet_arrival_report.write(3, 3, 'Departure Date', detailed_formate)
			# worksheet_arrival_report.set_column(3, 3, 22)
			# worksheet_arrival_report.write(3, 4, 'Departure Flight', detailed_formate)
			worksheet_arrival_report.set_column(8, 8, 22)
			worksheet_arrival_report.write(3, 8, 'Confirmation Number', detailed_formate)
			worksheet_arrival_report.set_column(9, 9, 22)
			worksheet_arrival_report.write(3, 9, 'Room Quantity', detailed_formate)
			worksheet_arrival_report.set_column(10, 10, 22)
			worksheet_arrival_report.write(3, 10, 'Room Type', detailed_formate)
			worksheet_arrival_report.set_column(11, 11, 22)
			worksheet_arrival_report.write(3, 11, 'Meal Plan', detailed_formate)
			worksheet_arrival_report.set_column(12, 12, 22)
			worksheet_arrival_report.write(3, 12, 'Transfer Type', detailed_formate)
			worksheet_arrival_report.set_column(13, 13, 22)
			worksheet_arrival_report.write(3, 13, 'Special Remarks', detailed_formate)
			worksheet_arrival_report.set_column(14, 14, 22)
			worksheet_arrival_report.write(3, 14, 'Applied Offer', detailed_formate)
			worksheet_arrival_report.set_column(15, 15, 22)
			worksheet_arrival_report.write(3, 15, 'Net Amount FC', detailed_formate)
			worksheet_arrival_report.freeze_panes(1, 0, 1, 0)
			line =4
			for data in arrival_dates: 
				line += 1
				# print(row)
				worksheet_arrival_report.write(line, 0, data['guest'])
				worksheet_arrival_report.write(line, 2, data['name'])
				worksheet_arrival_report.write(line, 3, data['hotel'])


			

				worksheet_arrival_report.write(line, 4, data['sub_agent'])
			   

				worksheet_arrival_report.write(line, 5, data['contract_no'])
				worksheet_arrival_report.write(line, 6, str(data['arrival_date']))
				worksheet_arrival_report.write(line, 7, str(data['arrival_flight']))
				# worksheet_arrival_report.write(line, 3, str(data['departure_date']))
				# worksheet_arrival_report.write(line, 4, data['departure_flight'])
				worksheet_arrival_report.write(line, 8, data['confirmation_no'])
				worksheet_arrival_report.write(line, 9, data['room_qty'])
				worksheet_arrival_report.write(line, 10, data['room_type'])
				worksheet_arrival_report.write(line, 11, data['meal_plan'])
				worksheet_arrival_report.write(line, 12, data['transfer_type'])
				worksheet_arrival_report.write(line, 13, data['special_remarks'])
				worksheet_arrival_report.write(line, 14, data['applied_offer'])
				worksheet_arrival_report.write(line, 15, data['fc_amount'])

		if departure_dates:
			
			cell_format = workbook.add_format({'bold': 1,'align': 'left', 'font_size':12, 'underline': True})
			headibng_format = workbook.add_format({'align': 'left', 'font_size': 15})
			worksheet_departure_report.set_row(0, 40)
			worksheet_departure_report.write(0, 5, 'Departure Date Report', cell_format)
			date = 'From: '+str(form)+' TO: '+ str(to)
			worksheet_departure_report.write(1, 5, date)
			worksheet_departure_report.set_row(4, 40)
			# worksheet_departure_report.write(hotel_row,1, x['agent'],headibng_format)
			worksheet_departure_report.set_row(4, 40)
			detailed_formate = workbook.add_format({'align': 'centre', 'font_size': 12,'bold': True, 'fg_color': '#DAD7DD', 'text_wrap': True})
			worksheet_departure_report.set_column(4, 40)
			worksheet_departure_report.set_column(0, 0,22)
			worksheet_departure_report.write(3, 0, 'Guest Name', detailed_formate)
			worksheet_departure_report.set_column(1, 1, 22)
			worksheet_departure_report.write(3, 1, 'Branch ', detailed_formate)
			worksheet_departure_report.set_column(2, 2, 22)
			worksheet_departure_report.write(3, 2, 'Reservations No', detailed_formate)
			worksheet_departure_report.set_column(3, 3, 22)
			worksheet_departure_report.write(3, 3, 'Hotel Name', detailed_formate)
			worksheet_departure_report.set_column(4, 4, 22)
			worksheet_departure_report.write(3, 4, 'Sub Agent', detailed_formate)

			# worksheet_departure_report.set_column(2, 2, 22)
			# worksheet_departure_report.write(3, 2, 'Arrival Flight', detailed_formate)
			worksheet_departure_report.set_column(5, 5, 22)
			worksheet_departure_report.write(3, 5, 'Contact Number', detailed_formate)
			worksheet_departure_report.set_column(6, 6, 22)
			worksheet_departure_report.write(3, 6, 'Departure Date', detailed_formate)
			worksheet_departure_report.set_column(7, 7, 22)
			worksheet_departure_report.write(3, 7, 'Departure Flight', detailed_formate)
			worksheet_departure_report.set_column(8, 8, 22)
			worksheet_departure_report.write(3, 8, 'Confirmation Number', detailed_formate)
			worksheet_departure_report.set_column(9, 9, 22)
			worksheet_departure_report.write(3, 9, 'Room Quantity', detailed_formate)
			worksheet_departure_report.set_column(10, 10, 22)
			worksheet_departure_report.write(3, 10, 'Room Type', detailed_formate)
			worksheet_departure_report.set_column(11, 11, 22)
			worksheet_departure_report.write(3, 11, 'Meal Plan', detailed_formate)
			worksheet_departure_report.set_column(12, 12, 22)
			worksheet_departure_report.write(3, 12, 'Transfer Type', detailed_formate)
			worksheet_departure_report.set_column(13, 13, 22)
			worksheet_departure_report.write(3, 13, 'Special Remarks', detailed_formate)
			worksheet_departure_report.set_column(14, 14, 22)
			worksheet_departure_report.write(3, 14, 'Applied Offer', detailed_formate)
			worksheet_departure_report.set_column(15, 15, 22)
			worksheet_departure_report.write(3, 15, 'Net Amount FC', detailed_formate)
			worksheet_departure_report.freeze_panes(1, 0, 1, 0)
			line =4
			for data in departure_dates: 
				line += 1
				# print(row)
				worksheet_departure_report.write(line, 0, data['guest'])
				worksheet_departure_report.write(line, 2, data['name'])
				worksheet_departure_report.write(line, 3, data['hotel'])


			

				worksheet_departure_report.write(line, 4, data['sub_agent'])
			   


				worksheet_departure_report.write(line, 5, data['contract_no'])
				# worksheet_departure_report.write(line, 1, str(data['arrival_date']))
				# worksheet_departure_report.write(line, 2, str(data['arrival_flight']))
				worksheet_departure_report.write(line, 6, str(data['departure_date']))
				worksheet_departure_report.write(line, 7, data['departure_flight'])
				worksheet_departure_report.write(line, 8, data['confirmation_no'])
				worksheet_departure_report.write(line, 9, data['room_qty'])
				worksheet_departure_report.write(line, 10, data['room_type'])
				worksheet_departure_report.write(line, 11, data['meal_plan'])
				worksheet_departure_report.write(line, 12, data['transfer_type'])
				worksheet_departure_report.write(line, 13, data['special_remarks'])
				worksheet_departure_report.write(line, 14, data['applied_offer'])
				worksheet_departure_report.write(line, 15, data['fc_amount'])
