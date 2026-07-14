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
import json
import urllib.parse
import urllib.request
from PIL import Image, ImageDraw

import xlsxwriter
from io import BytesIO
import xlsxwriter





class sub_client_report(models.AbstractModel):
	_name = 'report.sub_agent_report.sub_client_report'
	_description = 'Sub Client Report'

	@api.model
	def _get_report_values(self, docids, data=None):
		record_wizard = self.env['sub.client.report'].browse(self.env.context.get('active_ids'))

		form = record_wizard.form
		to = record_wizard.to
		typee = record_wizard.typee
		partner_id = record_wizard.partner_id
		payment_status = record_wizard.payment_status
		company = record_wizard.company_id or self.env.company
		translation_cache = {}
		brand_translation_map = {
			'togather travel': 'مؤسسة معا للسفر والسياحة',
		}

		def translate_to_ar(value):
			if not value:
				return ''
			value = str(value).strip()
			if not value:
				return ''
			mapped_value = brand_translation_map.get(value.lower())
			if mapped_value:
				return mapped_value
			if value in translation_cache:
				return translation_cache[value]
			try:
				params = urllib.parse.urlencode({
					'client': 'gtx',
					'sl': 'auto',
					'tl': 'ar',
					'dt': 't',
					'q': value,
				})
				url = 'https://translate.googleapis.com/translate_a/single?' + params
				with urllib.request.urlopen(url, timeout=5) as response:
					payload = json.loads(response.read().decode('utf-8'))
				translated = ''.join(part[0] for part in payload[0] if part and part[0])
				translation_cache[value] = translated or value
			except Exception:
				translation_cache[value] = value
			return translation_cache[value]


		if typee == 'all':
			partner = self.env['res.partner'].search([('travel_agency','=',False)])
		else:
			partner = []
			for x in partner_id:
				partner.append(x)

		agent_main_list = []
		agent_main_list_b2c  =[]    
		for x in partner:
			if payment_status == 'paid':
				payment_status_search = ('payment_state','=','paid')
				record = self.env['account.move'].search([('date','>=',form),('date','<=',to),('partner_id','=',x.id),('state','=','posted'),('move_type','=','out_invoice'),payment_status_search])
			if payment_status == 'in_payment':
				payment_status_search = ('payment_state','in',['in_payment','not_paid'])
				record = self.env['account.move'].search([('date','>=',form),('date','<=',to),('partner_id','=',x.id),('state','=','posted'),('move_type','=','out_invoice'),payment_status_search])
			if payment_status != 'in_payment' and payment_status != 'paid' :
				record = self.env['account.move'].search([('date','>=',form),('date','<=',to),('partner_id','=',x.id),('state','=','posted'),('move_type','=','out_invoice')])
			main_list = []
			for inv in record:
				package = self.env['reservation.order'].search([('name','=',inv.invoice_origin)])
				

				# Build a list of hotel names from both packages using list comprehensions
				hotels_list = []
				if package:
				    hotels_list += [hotel.hotel_id.name for hotel in package.hotel_pkg if hotel.hotel_id]
				

				# Join all hotel names with a "/" separator
				hotels_name = "/".join(hotels_list)

				print("Hotels Name:", hotels_name)

				main_list.append({
					'number':inv.name,
					'inv_date':inv.invoice_date,
					'hotels_name':hotels_name,
					'ref':inv.ref,
					'package_no':inv.package_no,
					'departure':inv.departure_date,
					'forgen':inv.foreign_currency,
					'arrival':inv.arrival_date,
					'tot_amt':inv.amount_total,
					'amount_due':inv.amount_residual,
					'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
					})
			print ("main_list")
			print (main_list)
			if main_list:
				
				agent_main_list.append({
					'agent':x.name,
					'currency':self.env.company.currency_id.symbol,
					'main_list':main_list,
					})
			

		payment_status_value = dict(record_wizard._fields['payment_status'].selection).get(record_wizard.payment_status)

		return {
			'doc_ids': docids,
			'doc_model':'account.move',
			'form': form,
			'to': to,
			'company': company,
			'translate_to_ar': translate_to_ar,
			'agent_main_list': agent_main_list,
			'payment_status_value': payment_status_value,
			# 'agent_main_list_b2c': agent_main_list_b2c,
		}







class sub_client_report_excel(models.AbstractModel):
	_name = 'report.sub_agent_report.sub_client_report.xslx'
	_inherit = 'report.report_xlsx.abstract'
	_description="Sub Client Report"





	def generate_xlsx_report(self, workbook, data, wizard_obj):



		record_wizard = self.env['sub.client.report'].browse(self.env.context.get('active_ids'))
		form = record_wizard.form
		to = record_wizard.to
		typee = record_wizard.typee
		partner_id = record_wizard.partner_id
		payment_status = record_wizard.payment_status
		company = record_wizard.company_id
		if typee == 'all':
			partner = self.env['res.partner'].search([('travel_agency','=',False)])
		else:
			partner = []
			for x in partner_id:
				partner.append(x)

		agent_main_list = []
		for x in partner:

			if payment_status == 'paid':
				payment_status_search = ('payment_state','=','paid')
				record = self.env['account.move'].search([('date','>=',form),('date','<=',to),('partner_id','=',x.id),('state','=','posted'),('move_type','=','out_invoice'),payment_status_search])
			if payment_status == 'in_payment':
				payment_status_search = ('payment_state','in',['in_payment','not_paid','partial'])
				record = self.env['account.move'].search([('date','>=',form),('date','<=',to),('partner_id','=',x.id),('state','=','posted'),('move_type','=','out_invoice'),payment_status_search])
			if payment_status != 'in_payment' and payment_status != 'paid' :
				record = self.env['account.move'].search([('date','>=',form),('date','<=',to),('partner_id','=',x.id),('state','=','posted'),('move_type','=','out_invoice')])
			
			main_list = []

			for inv in record:
				package = self.env['reservation.order'].search([('name','=',inv.invoice_origin)])
				hotels_name = ""
				for hotel in package.hotel_pkg:
					if hotel.hotel_id:
						if not hotels_name:
							hotels_name = hotel.hotel_id.name
						else:
							hotels_name = hotels_name+"/"+hotel.hotel_id.name

				main_list.append({
					'number':inv.name,
					'inv_date':inv.invoice_date,
					'hotels_name':hotels_name,
					'ref':inv.ref,
					'package_no':inv.package_no,
					'departure':inv.departure_date,
					'forgen':inv.foreign_currency,
					'arrival':inv.arrival_date,
					'tot_amt':inv.amount_total,
					'amount_due':inv.amount_residual,
					'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
					})
			if main_list:
				agent_main_list.append({
					'agent':x.name,
					'currency':company.currency_id.symbol,
					'main_list':main_list,
					})




		if agent_main_list:
			hotel_row = 2
			row = 3
			for x in agent_main_list:


				worksheet_agent_report = workbook.add_worksheet(x['agent'])
				cell_format = workbook.add_format({'bold': 1,'align': 'left', 'font_size': 20, 'underline': True})
				headibng_format = workbook.add_format({'align': 'left', 'font_size': 15})
				worksheet_agent_report.set_row(0, 40)
				worksheet_agent_report.write(0, 5, 'Sub Client Report', cell_format)
				date = 'From: '+str(form)+' TO: '+ str(to)
				worksheet_agent_report.write(1, 5, date)
				worksheet_agent_report.set_row(4, 40)
				worksheet_agent_report.write(hotel_row,1, x['agent'],headibng_format)
				worksheet_agent_report.set_row(4, 40)
				detailed_formate = workbook.add_format({'align': 'centre', 'font_size': 12,'underline': True,'bold': True, 'fg_color': '#DAD7DD', 'text_wrap': True})
				worksheet_agent_report.set_column(4, 40)
				worksheet_agent_report.set_column(0, 0,20)
				worksheet_agent_report.write(row, 0, 'Invoice No', detailed_formate)
				worksheet_agent_report.set_column(1, 1, 20)
				worksheet_agent_report.write(row, 1, 'Branch', detailed_formate)
				worksheet_agent_report.set_column(2, 2, 20)
				worksheet_agent_report.write(row, 2, 'Invoice Date', detailed_formate)
				worksheet_agent_report.set_column(3, 3, 20)
				worksheet_agent_report.write(row, 3, 'Hotel(s)', detailed_formate)
				worksheet_agent_report.set_column(4, 4, 20)
				worksheet_agent_report.write(row, 4, 'Ref/Cust Name', detailed_formate)
				worksheet_agent_report.set_column(5, 5, 20)
				worksheet_agent_report.write(row, 5, 'Package No', detailed_formate)
				worksheet_agent_report.set_column(6,6, 20)
				worksheet_agent_report.write(row, 6, 'Arrival Date', detailed_formate)
				worksheet_agent_report.set_column(7, 7, 20)
				worksheet_agent_report.write(row, 7, 'Departure Date', detailed_formate)
				worksheet_agent_report.set_column(8, 8, 20)
				worksheet_agent_report.write(row, 8, 'Amount FC', detailed_formate)
				worksheet_agent_report.set_column(9, 9, 20)
				worksheet_agent_report.write(row, 9, 'Total Amount', detailed_formate)
				worksheet_agent_report.set_column(10, 10, 20)
				worksheet_agent_report.write(row, 10, 'Amount Due', detailed_formate)
				worksheet_agent_report.set_column(11, 11, 20)
				worksheet_agent_report.write(row, 11, 'Invoice Status', detailed_formate)
				worksheet_agent_report.freeze_panes(1, 0, 1, 0)
				line = row
				total_amount = 0
				total_amount_due = 0
				for data in x['main_list']: 
					line += 1
					worksheet_agent_report.write(line, 0, data['number'])
					worksheet_agent_report.write(line, 2, str(data['inv_date']))
					worksheet_agent_report.write(line, 3, data['hotels_name'])
					worksheet_agent_report.write(line, 4, data['ref'])
					worksheet_agent_report.write(line, 5, data['package_no'])
					worksheet_agent_report.write(line, 6, str(data['arrival']))
					worksheet_agent_report.write(line, 7, str(data['departure']))
					worksheet_agent_report.write(line, 8, data['forgen'])
					worksheet_agent_report.write(line, 9, data['tot_amt'])
					worksheet_agent_report.write(line, 10, data['amount_due'])
					worksheet_agent_report.write(line, 11, data['status'])
					total_amount += data['tot_amt']
					total_amount_due += data['amount_due']
				line += 1
				worksheet_agent_report.set_column(line, 40,20)
				worksheet_agent_report.write(line, 0, 'Total', detailed_formate)
				worksheet_agent_report.set_column(1, 1, 20)
				worksheet_agent_report.write(line, 1, '', detailed_formate)
				worksheet_agent_report.set_column(2, 2, 20)
				worksheet_agent_report.write(line, 2, '', detailed_formate)
				worksheet_agent_report.set_column(3, 3, 20)
				worksheet_agent_report.write(line, 3, '', detailed_formate)
				worksheet_agent_report.set_column(4, 4, 20)
				worksheet_agent_report.write(line, 4, '', detailed_formate)
				worksheet_agent_report.set_column(5, 5, 20)
				worksheet_agent_report.write(line, 5, '', detailed_formate)
				worksheet_agent_report.set_column(6, 6, 20)
				worksheet_agent_report.write(line, 6, '', detailed_formate)
				worksheet_agent_report.set_column(7, 7, 20)
				worksheet_agent_report.write(line, 7, '', detailed_formate)
				worksheet_agent_report.set_column(8, 8, 20)
				worksheet_agent_report.write(line, 8, '', detailed_formate)
				worksheet_agent_report.set_column(9, 9, 20)
				worksheet_agent_report.write(line, 9, total_amount, detailed_formate)
				worksheet_agent_report.set_column(10, 10, 20)
				worksheet_agent_report.write(line, 10, total_amount_due, detailed_formate)
				worksheet_agent_report.set_column(11, 11, 20)
				worksheet_agent_report.write(line, 11, '', detailed_formate)