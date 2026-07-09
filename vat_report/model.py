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


class vat_report(models.AbstractModel):
	_name = 'report.vat_report.vat_report'
	_description = 'Vat Report'

	@api.model
	def _get_report_values(self, docids, data=None):
		record_wizard = self.env['vat.report'].browse(self.env.context.get('active_ids'))

		form = record_wizard.form
		to = record_wizard.to
		company = record_wizard.company_id


		sale_pur_record = self.env['account.move'].search([('date','>=',form),('date','<=',to),('state','=','posted')])
		tax = self.env['account.tax'].search([('type_tax_use','=','sale')],limit=1)
		# expense_account = self.env['account.account'].search([('user_type_id.name','=','Expenses')],limit=1)

		expense_record = self.env['account.move.line'].search([('move_id.date','>=',form),('move_id.date','<=',to),('move_id.move_type','=','entry'),('move_id.state','=','posted'),('account_id.account_type','=','expense'),('account_id.name','!=','Tax Expense')])


		print (expense_record)
		debit = 0
		credit = 0
		expense_list = []
		for x in expense_record:
			debit += x.debit
			credit += x.credit
			expense_list.append({
				'bill_no':x.move_id.name,
				'bill_date':x.move_id.date,
				'debit':x.debit,
				'credit':x.credit,
				'status':x.move_id.state,
				})

		sale_amt = 0
		pur_amt = 0
		profit_after_expen =0
		sale_list = []
		purchase_list = []
		for x in sale_pur_record:
			if x.move_type == 'out_invoice':
				sale_amt += x.amount_total
				sale_list.append({
					'invoice_no':x.name,
					'invoice_date':x.invoice_date,
					'customer':x.partner_id.name,
					'total_amount':x.amount_total,
					'amount_Due':x.amount_residual,
					'status':dict(x._fields['payment_state'].selection).get(x.payment_state),
				})
			if x.move_type == 'in_invoice':
				purchase_list.append({
					'invoice_no':x.name,
					'invoice_date':x.invoice_date,
					'customer':x.partner_id.name,
					'total_amount':x.amount_total,
					'amount_Due':x.amount_residual,
					'status':dict(x._fields['payment_state'].selection).get(x.payment_state),
				})
				pur_amt += x.amount_total

		gross_profit = sale_amt - pur_amt
		expense = debit - credit
		profit_after_expen = gross_profit - expense
		vat_amt = (profit_after_expen * tax.amount) / 100
		pat_amt = profit_after_expen - vat_amt
		pnl_amt = pat_amt 

		return {
			'doc_ids': docids,
			'doc_model':'account.move',
			'form': form,
			'to': to,
			'company': company,
			'sale_amt': sale_amt,
			'pur_amt': pur_amt,
			'gross_profit': gross_profit,
			'vat_amt': vat_amt,
			'pat_amt': pat_amt,
			'expense': expense,
			'pnl_amt': pnl_amt,
			'profit_after_expen':profit_after_expen,
			'expense_list':expense_list,
			'sale_list':sale_list,
			'purchase_list':purchase_list,
		}




class vat_report_xlsx(models.AbstractModel):
	_name = 'report.vat_report.vat_report_xlsx'
	_inherit = 'report.report_xlsx.abstract'
	_description="Vat Report"





	def generate_xlsx_report(self, workbook, data, wizard_obj):



		record_wizard = self.env['vat.report'].browse(self.env.context.get('active_ids'))
		form = record_wizard.form
		to = record_wizard.to
		company = record_wizard.company_id


		company = self.env['res.company'].search([], limit=1)
		sale_pur_record = self.env['account.move'].search(
			[('date', '>=', form), ('date', '<=', to), ('state', '=', 'posted')])
		tax = self.env['account.tax'].search([('type_tax_use', '=', 'sale')], limit=1)
		expense_record = self.env['account.move.line'].search(
			[('move_id.date', '>=', form), ('move_id.date', '<=', to), ('move_id.move_type', '=', 'entry'),
			 ('move_id.state', '=', 'posted'), ('account_id.account_type','=','expense'),
			 ('account_id.name', '!=', 'Tax Expense')])

		###############calculating expenses ##################################
		debit = 0
		credit = 0
		expense_list = []
		for x in expense_record:
			debit += x.debit
			credit += x.credit
			expense_list.append({
				'bill_no': x.move_id.name,
				'bill_date': x.move_id.date,
				'debit': x.debit,
				'credit': x.credit,
				'status': x.move_id.state,
			})
		#################calculating sales and purchase##########
		sale_amt = 0
		pur_amt = 0
		profit_after_expen = 0
		sale_list = []
		purchase_list = []
		for x in sale_pur_record:
			if x.move_type == 'out_invoice':
				sale_amt += x.amount_total
				sale_list.append({
					'invoice_no': x.name,
					'invoice_date': x.invoice_date,
					'customer': x.partner_id.name,
					'total_amount': x.amount_total,
					'amount_Due': x.amount_residual,
					'status': dict(x._fields['payment_state'].selection).get(x.payment_state),
				})
			if x.move_type == 'in_invoice':
				purchase_list.append({
					'invoice_no': x.name,
					'invoice_date': x.invoice_date,
					'customer': x.partner_id.name,
					'total_amount': x.amount_total,
					'amount_Due': x.amount_residual,
					'status': dict(x._fields['payment_state'].selection).get(x.payment_state),
				})
				pur_amt += x.amount_total

		gross_profit = sale_amt - pur_amt
		expense = debit - credit
		profit_after_expen = gross_profit - expense
		vat_amt = (profit_after_expen * tax.amount) / 100
		pat_amt = profit_after_expen - vat_amt
		pnl_amt = pat_amt

		worksheet_summery = workbook.add_worksheet('Summery')
		worksheet_sale = workbook.add_worksheet('Sale')
		worksheet_cost_of_goods_sold = workbook.add_worksheet('Cost of Goods Sold')
		worksheet_expense = workbook.add_worksheet('Expense')
		h4_bold = workbook.add_format({'bold': True, 'align': 'left', 'font_size': 10})
		worksheet_summery.write(1, 1, company.name, h4_bold)
		worksheet_summery.write(2, 1, company.street, h4_bold)
		worksheet_summery.write(3, 1, company.street2, h4_bold)
		worksheet_summery.write(4, 1, company.city, h4_bold)
		worksheet_summery.write(5, 1, company.country_id.name, h4_bold)
		worksheet_summery.write(6, 1, 'CR No:', h4_bold)
		worksheet_summery.write(6, 2, company.company_registry, h4_bold)
		worksheet_summery.write(7, 1, 'Ph:', h4_bold)
		worksheet_summery.write(7, 2, company.phone, h4_bold)
		worksheet_summery.write(8, 1, 'Company Email:', h4_bold)
		worksheet_summery.write(8, 2, company.email, h4_bold)
		worksheet_summery.write(9, 1, 'vat', h4_bold)
		worksheet_summery.write(9, 2, company.vat, h4_bold)
		cell_format = workbook.add_format({'align': 'left', 'font_size': 10, 'underline': True})
		worksheet_summery.set_row(10, 25)
		worksheet_summery.write(10, 2, 'VAT Report or P&L', cell_format)

		cell_format = workbook.add_format({'align': 'centre', 'font_size': 10,
										   'underline': True, 'bold': True, 'fg_color': '#eaded7',
										   'text_wrap': True})
		worksheet_summery.set_row(12, 40)
		worksheet_summery.write(12, 0, 'Sale', cell_format)
		worksheet_summery.set_column(1, 1, 20)
		worksheet_summery.write(12, 1, 'Cost Of \nGoods Sold', cell_format)
		worksheet_summery.set_column(2, 2, 15)
		worksheet_summery.write(12, 2, 'Gross Profit', cell_format)
		worksheet_summery.set_column(3, 3, 15)
		worksheet_summery.write(12, 3, 'Expenses', cell_format)
		worksheet_summery.set_column(4, 4, 22)
		worksheet_summery.write(12, 4, 'Profit after \nExpense(PAE)', cell_format)
		worksheet_summery.set_column(5, 5, 10)
		worksheet_summery.write(12, 5, 'VAT%', cell_format)
		worksheet_summery.set_column(6, 6, 10)
		worksheet_summery.write(12, 6, 'PAT', cell_format)
		worksheet_summery.set_column(7, 7, 15)
		worksheet_summery.write(12, 7, 'Profit/Loss', cell_format)


		worksheet_summery.write(13, 0, sale_amt)
		worksheet_summery.write(13, 1, pur_amt)
		worksheet_summery.write(13, 2, gross_profit)
		worksheet_summery.write(13, 3, expense)
		worksheet_summery.write(13, 4, profit_after_expen)
		worksheet_summery.write(13, 5, vat_amt)
		worksheet_summery.write(13, 6, pat_amt)
		worksheet_summery.write(13, 7, pnl_amt)




		####################################################################
		######################### Data for summery ENDS HERE #########################
		####################################################################

		##########################################################################
		####################### Data for sale Starts ########################
		######################################################################

		worksheet_sale.set_row(0, 40)
		sale_format = workbook.add_format({'align': 'centre', 'font_size': 10,'underline': True,
										   'bold': True, 'fg_color': '#eaded7', 'text_wrap': True})
		worksheet_sale.set_column(0, 0, 15)
		worksheet_sale.write(0, 0, 'Invoice No	', sale_format)
		worksheet_sale.set_column(1, 1, 15)
		worksheet_sale.write(0, 1, 'Branch', sale_format)
		worksheet_sale.set_column(2, 2, 15)
		worksheet_sale.write(0, 2, 'Invoice Date', sale_format)
		worksheet_sale.set_column(3, 3, 25)
		worksheet_sale.write(0, 3, 'Customer', sale_format)
		worksheet_sale.set_column(4, 4, 15)
		worksheet_sale.write(0, 4, 'Total Amount', sale_format)
		worksheet_sale.set_column(5, 5, 15)
		worksheet_sale.write(0, 5, 'Amount Due', sale_format)
		worksheet_sale.set_column(6, 6, 15)
		worksheet_sale.write(0, 6, 'Invoice Status', sale_format)
		worksheet_sale.freeze_panes(1, 0, 1, 0)

		row = 0
		grand_total_sale=0
		grand_total_amnt_due=0
		for sales in sale_list:
			row += 1
			# print(row)
			worksheet_sale.write(row, 0, sales['invoice_no'])
			worksheet_sale.write(row, 2, str(sales['invoice_date']))
			worksheet_sale.write(row, 3, sales['customer'])
			worksheet_sale.write(row, 4, sales['total_amount'])
			worksheet_sale.write(row, 5, sales['amount_Due'])
			worksheet_sale.write(row, 6, sales['status'])
			grand_total_sale=grand_total_sale+sales['total_amount']
			grand_total_amnt_due = grand_total_amnt_due + sales['amount_Due']

			##########################################################################
			####################### Data for sale Starts ENDS HERE########################
			######################################################################

		##########################################################################
		####################### Data for Cost Of Goods Sold ########################
		######################################################################
		worksheet_cost_of_goods_sold.set_row(0, 40)
		sale_format = workbook.add_format({'align': 'centre', 'font_size': 10,'underline': True,
										   'bold': True, 'fg_color': '#eaded7', 'text_wrap': True})
		worksheet_cost_of_goods_sold.set_column(0, 0, 15)
		worksheet_cost_of_goods_sold.write(0, 0, 'Bill No', sale_format)
		worksheet_cost_of_goods_sold.set_column(1, 1, 15)
		worksheet_cost_of_goods_sold.write(0, 1, 'Branch', sale_format)
		worksheet_cost_of_goods_sold.set_column(2, 2, 15)
		worksheet_cost_of_goods_sold.write(0, 2, 'Bill Date', sale_format)
		worksheet_cost_of_goods_sold.set_column(3, 3, 25)
		worksheet_cost_of_goods_sold.write(0, 3, 'Vendor', sale_format)
		worksheet_cost_of_goods_sold.set_column(4, 4, 15)
		worksheet_cost_of_goods_sold.write(0, 4, 'Total Amount', sale_format)
		worksheet_cost_of_goods_sold.set_column(5, 5, 15)
		worksheet_cost_of_goods_sold.write(0, 5, 'Amount Due', sale_format)
		worksheet_cost_of_goods_sold.set_column(6, 6, 15)
		worksheet_cost_of_goods_sold.write(0, 6, 'Bill Status', sale_format)
		worksheet_cost_of_goods_sold.freeze_panes(1, 0, 1, 0)

		row = 0
		grand_total_purchase = 0
		grand_total_amnt_due_purchase= 0
		for purchase in purchase_list:
			row += 1
			# print(row)
			worksheet_cost_of_goods_sold.write(row, 0, purchase['invoice_no'])
			worksheet_cost_of_goods_sold.write(row, 2, str(purchase['invoice_date']))
			worksheet_cost_of_goods_sold.write(row, 3, purchase['customer'])
			worksheet_cost_of_goods_sold.write(row, 4, purchase['total_amount'])
			worksheet_cost_of_goods_sold.write(row, 5, purchase['amount_Due'])
			worksheet_cost_of_goods_sold.write(row, 6, purchase['status'])
			grand_total_purchase = grand_total_purchase + purchase['total_amount']
			grand_total_amnt_due_purchase = grand_total_amnt_due_purchase + purchase['amount_Due']

			##########################################################################
			####################### Data for Cost Of Goods Sold ENDS HERE ########################
			######################################################################

		#################################################################################
		###################### Data for Expense Starts Here ############################
		##############################################################################

		worksheet_expense.set_row(0, 40)
		expense_fromat = workbook.add_format({'align': 'centre', 'font_size': 10,'underline': True,
										   'bold': True, 'fg_color': '#eaded7', 'text_wrap': True})
		worksheet_expense.set_column(0, 0, 15)
		worksheet_expense.write(0, 0, 'Bill No', expense_fromat)
		worksheet_expense.set_column(1, 1, 15)
		worksheet_expense.write(0, 1, 'Branch', expense_fromat)
		worksheet_expense.set_column(2, 2, 15)
		worksheet_expense.write(0, 2, 'Bill Date', expense_fromat)
		worksheet_expense.set_column(3, 3, 15)
		worksheet_expense.write(0, 3, 'Debit', expense_fromat)
		worksheet_expense.set_column(4, 4, 15)
		worksheet_expense.write(0, 4, 'Credit', expense_fromat)
		worksheet_expense.set_column(5, 5, 15)
		worksheet_expense.write(0, 5, 'Status', expense_fromat)
		worksheet_expense.freeze_panes(1, 0, 1, 0)

		row = 0
		for expense in expense_list:
			row += 1
			worksheet_expense.write(row, 0, expense['bill_no'])
			worksheet_expense.write(row, 2, str(expense['bill_date']))
			worksheet_expense.write(row, 3, expense['debit'])
			worksheet_expense.write(row, 4, expense['credit'])
			worksheet_expense.write(row, 5, expense['status'])

			#################################################################################
			###################### Data for Expense ENDS HERE ############################
			##############################################################################