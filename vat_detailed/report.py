#-*- coding:utf-8 -*-
########################################################################################
########################################################################################
##                                                                                    ##
##    Odoo13                                                                          ##
##    Copyright (C) 2019 odoo13  (<http://ecube.pk>). All Rights Reserved             ##
##    contact us  at                                   for your erp needs.            ##
## Odoo is an all-in-one business software including CRM, e-commerce, accounting,MRP, ##
## Project management, and inventory. It helps you to improve the quality and         ##
## efficiency of your business.                                                       ##
########################################################################################
########################################################################################

from odoo import models, fields, api
from datetime import date
from datetime import datetime, date, timedelta
from collections import namedtuple
from odoo.exceptions import ValidationError
import json
import os
import xlsxwriter
from io import BytesIO
import datetime
import time
from odoo.tools import config
import base64
import string
import sys
import logging

_logger = logging.getLogger(__name__)
import xlsxwriter


class vat_detailed_xlsx(models.AbstractModel):
	_name = 'report.vat_detailed.vat_detailed.xlsx'
	_inherit = 'report.report_xlsx.abstract'
	_description="Employee Commission"





	def generate_xlsx_report(self, workbook, data, wizard_obj):

		################################ caculated values for excel report ##########
		############################################################################

		main_list = []
		for rec in wizard_obj:
			date_from = rec.date_from
			employee_id = rec.employee_id.name
			date_to = rec.date_to
			sale = rec.sale
			cost_goods_sold = rec.cost_goods_sold
			gross_profit = rec.gross_profit
			vat_amt = rec.vat
			pat = rec.pat
			expenses = rec.expenses
			profit_loss = rec.profit_loss
			percentage = rec.percentage
			commission = rec.commission
			vendor_bill = rec.vendor_bill
			state = dict(rec._fields['state'].selection).get(rec.state)

			child_main_list = []
			for vat in rec.vat_detail:
				hotel_name = ''
				for hotel in vat.hotel_ids:
					hotel_name = hotel.name + ',' + hotel_name

				child_main_list.append({
					'employee':vat.employee.name,
					'percentage':vat.percentage,
					'voucher':vat.voucher,
					'journal_entry':vat.journal_entry.name,
					'commission':vat.commission,
					'arrival_date':vat.arrival_date,
					'departure_date':vat.departure_date,
					'hotel_ids':hotel_name,
					'invoice_payment_state':dict(vat.journal_entry._fields['payment_state'].selection).get(vat.journal_entry.payment_state),
					'partner_id':vat.partner_id.name,
					'salesperson':vat.salesperson.name,
					})

			main_list.append({
				'date_from':date_from,
				'employee_id':employee_id,
				'date_to':date_to,
				'sale':sale,
				'cost_goods_sold':cost_goods_sold,
				'gross_profit':gross_profit,
				'vat':vat_amt,
				'pat':pat,
				'expenses':expenses,
				'profit_loss':profit_loss,
				'percentage':percentage,
				'commission':commission,
				'vendor_bill':vendor_bill,
				'state':state,
				'child_main_list':child_main_list,
				})


			if main_list:
				employee_commission = workbook.add_worksheet('Employee Commission')

			##########################################################################
			####################### Data for Hotel Detailed Starts ########################
			######################################################################
			for x in main_list:
				cell_format = workbook.add_format({'align': 'left', 'font_size': 20, 'underline': True})
				headibng_format = workbook.add_format({'align': 'left', 'font_size': 15})
				employee_commission.set_row(0, 40)
				employee_commission.write(0, 3, 'Employee Commission', cell_format)
				
				h4_bold = workbook.add_format({'bold': True, 'align': 'left', 'font_size': 10})
				employee_commission.write(1, 1, 'From:', h4_bold)
				employee_commission.write(1, 2, x['date_from'], h4_bold)
				employee_commission.write(2, 1, 'Employee:', h4_bold)
				employee_commission.write(2, 2, x['employee_id'], h4_bold)
				employee_commission.write(3, 1, 'Sale', h4_bold)
				employee_commission.write(3, 2, x['sale'], h4_bold)
				employee_commission.write(4, 1, 'Cost of Goods Sold', h4_bold)
				employee_commission.write(4, 2, x['cost_goods_sold'], h4_bold)
				employee_commission.write(5, 1, 'Gross Profit', h4_bold)
				employee_commission.write(5, 2, x['gross_profit'], h4_bold)
				employee_commission.write(6, 1, 'VAT', h4_bold)
				employee_commission.write(6, 2, x['vat'], h4_bold)
				# employee_commission.write(2, 4, 'Expenses', h4_bold)
				# employee_commission.write(2, 5, x['expenses'], h4_bold)
				employee_commission.write(1, 4, 'To:', h4_bold)
				employee_commission.write(1, 5, x['date_to'], h4_bold)
				employee_commission.write(2, 4, 'PAT', h4_bold)
				employee_commission.write(2, 5, x['pat'], h4_bold)
				employee_commission.write(3, 4, 'Profit/Loss', h4_bold)
				employee_commission.write(3, 5, x['profit_loss'], h4_bold)
				employee_commission.write(4, 4, 'Percentage', h4_bold)
				employee_commission.write(4, 5, x['percentage'], h4_bold)
				employee_commission.write(5, 4, 'Commission', h4_bold)
				employee_commission.write(5, 5, x['commission'], h4_bold)
				employee_commission.write(6, 4, 'Status', h4_bold)
				employee_commission.write(6, 5, x['state'], h4_bold)
				cell_format = workbook.add_format({'align': 'left', 'font_size': 10, 'underline': True})
				employee_commission.set_row(10, 25)

				employee_commission.set_row(4, 40)
				detailed_formate = workbook.add_format({'align': 'centre', 'font_size': 12,'underline': True,'bold': True, 'fg_color': '#DAD7DD', 'text_wrap': True})
				employee_commission.set_column(4, 40)
				employee_commission.write(10, 1, 'Voucher No', detailed_formate)

				employee_commission.write(10, 2, 'Arrival Date', detailed_formate)
				employee_commission.write(10, 3, 'Departure Date', detailed_formate)
				employee_commission.write(10, 4, 'Hotel', detailed_formate)
				employee_commission.merge_range(10, 5,10, 6, 'Customer', detailed_formate)
				employee_commission.set_column(1, 1, 22)
				employee_commission.merge_range(10, 7,10, 8, 'Invoices', detailed_formate)
				employee_commission.set_column(2, 2, 22)
				employee_commission.merge_range(10, 9,10, 10, 'Invoice Status', detailed_formate)
				employee_commission.set_column(3, 3, 22)
				employee_commission.merge_range(10, 11,10, 12, 'Inv/Bill Total', detailed_formate)
				employee_commission.set_column(4, 4, 22)
				employee_commission.merge_range(10, 13,10, 14, 'Salesperson', detailed_formate)
				employee_commission.set_column(5, 5, 22)
				employee_commission.freeze_panes(1, 0, 1, 0)
				line = 10
				for data in x['child_main_list']: 
					line += 1
					employee_commission.write(line, 1, data['voucher'])
					employee_commission.write(line, 2, data['arrival_date'])
					employee_commission.write(line, 3, data['departure_date'])
					employee_commission.write(line, 4, data['hotel_ids'])
					employee_commission.merge_range(line, 5,line, 6, data['partner_id'])
					employee_commission.merge_range(line, 7,line, 8, data['journal_entry'])
					employee_commission.merge_range(line, 9,line, 10, data['invoice_payment_state'])
					employee_commission.merge_range(line, 11,line, 12, str(data['commission']))
					employee_commission.merge_range(line, 13,line, 14, str(data['salesperson']))
				line += 1