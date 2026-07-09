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



class vat_detailed(models.Model):
    _name = 'vat.detailed'
    _rec_name = 'employee_id'
    _description = "Vat Detail"

    date_from = fields.Date('From',required=True)
    employee_id = fields.Many2one('hr.employee','Employee',required=True)
    date_to = fields.Date('To',required=True)
    sale = fields.Float(string='Sale')
    cost_goods_sold = fields.Float(string='Cost of Goods Sold')
    gross_profit = fields.Float(string='Gross Profit')
    vat = fields.Float(string='VAT')
    pat = fields.Float(string='PAT')
    expenses = fields.Float(string='Expenses')
    profit_loss = fields.Float(string='Profit/Loss')
    percentage = fields.Float(string='Percentage')
    commission = fields.Float(string='Commission')
    vat_detail = fields.One2many('vat.detailed.tree','tree_link')
    vendor_bill = fields.Many2one('account.move','Vendor Bill')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ], 'State', default='draft')

    

    @api.onchange('employee_id')
    def get_percentage(self):
        if self.employee_id:
            self.percentage = self.employee_id.percentage
            

    def unlink(self):
        for rec in self:
            if rec.state == 'validated':
                raise ValidationError("Can't delete a validated entry!")
        rec = super(vat_detailed, self).unlink()

        return rec

    def daterange_overlap_check(self, r1, r2):
        r1 = Range(start=datetime(2012, 1, 15), end=datetime(2012, 5, 10))
        r2 = Range(start=datetime(2012, 3, 20), end=datetime(2012, 9, 15))
        latest_start = max(r1.start, r2.start)
        earliest_end = min(r1.end, r2.end)
        delta = (earliest_end - latest_start).days + 1
        overlap = max(0, delta)


    def get_invoices(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('date','>=',self.date_from),('date','<=',self.date_to),('state','=','posted'),('invoice_user_id','=',self.employee_id.user_id.id),('is_commissioned','=',False)]
        }

    def excel_report(self):
        self.env.ref('vat_detailed.report_for_vat_detailed_xlsx').report_file = 'Employee Commission Report' + ' ' + str(fields.Date.today())
        return self.env.ref('vat_detailed.report_for_vat_detailed_xlsx').report_action(self)
        # ################################ caculated values for excel report ##########
        # ############################################################################

   

    def set_jes(self):
         je_recs = self.env['account.move'].search([('is_commissioned','=',True)])
         for x in je_recs:
            x.is_commissioned = False

    def set_commissioned_field(self):
         je_recs = self.env['account.move'].search([('package_no','!=',False)])
         for x in je_recs:
            so = self.env['reservation.order'].search([('name','=',x.package_no)])
            if so:

                x.commissioned = so.commissioned

    def cancel_commission(self):
        if self.state == 'validated':
            if self.vendor_bill:
                self.vendor_bill.unlink()

            if self.vat_detail:
                for vat in self.vat_detail:
                    vat.journal_entry.is_commissioned = False
                    vat.unlink()
            self.state = 'draft'


    def get_data(self):
        sale_pur_record = self.env['account.move'].search([('invoice_date','>=',self.date_from),('invoice_date','<=',self.date_to),('state','=','posted'),('commissioned','=',True),('invoice_user_id','=',self.employee_id.user_id.id),('is_commissioned','=',False),('move_type','in',['out_invoice','in_invoice','out_refund','in_refund'])])
       
        tax = self.env['account.tax'].search([('type_tax_use','=','sale')],limit=1)
        expense_account = self.env['account.account'].search([('account_type','=','expense')],limit=1)

        expense_record = self.env['account.move'].search([('invoice_date','>=',self.date_from),('invoice_date','<=',self.date_to),('state','=','posted'),('commissioned','=',True),('invoice_user_id','=',self.employee_id.user_id.id),('is_commissioned','=',False),('move_type','in',['out_invoice','in_invoice','out_refund','in_refund'])])

        if not sale_pur_record:
            raise ValidationError("No commissionable record against selected employee within givin dates")

        
        debit = 0
        credit = 0
        for rec in expense_record:
            for x in rec.line_ids:
                if x.account_id.id == expense_account.id:
                    debit += x.debit
                    credit += x.credit
            
        sale_amt = 0
        pur_amt = 0
        for x in sale_pur_record:
            if x.move_type == 'out_invoice':
                sale_amt += x.amount_total
            if x.move_type == 'in_invoice':
                pur_amt += x.amount_total
            if x.move_type == 'out_refund':
                pur_amt += x.amount_total
            if x.move_type == 'in_refund':
                sale_amt += x.amount_total

            x.is_commissioned = True
        gross_profit = sale_amt - pur_amt
        vat_amt = (gross_profit * tax.amount) / 100
        pat_amt = gross_profit - vat_amt
        expense = debit - credit
        commsion_amt = pat_amt * self.percentage / 100
        # commsion = pat_amt - commsion_amt
        self.sale = sale_amt
        self.cost_goods_sold = pur_amt
        self.gross_profit = gross_profit
        self.vat = vat_amt
        self.pat = pat_amt
        self.expenses = expense
        self.commission = (self.pat * self.employee_id.percentage) / 100

        if self.vat_detail:
            for x in self.vat_detail:
                x.unlink()

        data = self.env['vat.detailed.tree']
        for x in sale_pur_record:
            amt = 0
            if x.move_type == 'out_invoice':
                amt = x.amount_total
            elif x.move_type == 'in_invoice':
                amt = -(x.amount_total)
            elif x.move_type == 'out_refund':
                amt = -(x.amount_total)
            elif x.move_type == 'in_refund':
                amt = x.amount_total
            else:
                amt = 0
            # if amt > 0:
            hotel_list = []
            for hotel in x.hotel_ids:
                hotel_list.append(hotel.id)
            # if 

            record = data.create({
                'commission':amt,
                'voucher':x.package_no,
                'salesperson':x.invoice_user_id.id,
                'journal_entry':x.id,
                'arrival_date':x.arrival_date,
                'departure_date':x.departure_date,
                'hotel_ids':x.hotel_ids.ids,
                'partner_id':x.partner_id.id,
                'tree_link':self.id,
            })
       
        pnl_amt = pat_amt - expense - commsion_amt
        self.profit_loss = pnl_amt
        self.state = 'validated'
        self.create_vendor_bill()

    def create_vendor_bill(self):
        journal_id = self.env['account.journal'].search([('type','=','purchase')],limit=1)
        if not journal_id:
            raise ValidationError("No Journal With type 'Purchase' exist")
        product = self.env['product.product'].search([('name','=','Commission')],limit=1)
        line_ids = []
        line_ids.append(
            (0,0, {
                'product_id': product.id,
                'name': product.name,
                'account_id': journal_id.default_account_id.id,
                'quantity':1,
                'price_unit':self.commission,
                # 'move_id':create_vendor_bill.id,
            }))
        create_vendor_bill = self.env['account.move'].create({
            'journal_id': journal_id.id,
            'invoice_date': fields.date.today(),
            'date': fields.date.today(),
            'move_type': 'in_invoice',
            'partner_id':self.employee_id.user_partner_id.id,
            'invoice_line_ids':line_ids,
            })
        self.vendor_bill = create_vendor_bill.id

       

class vat_detailed_tree(models.Model):
    _name = 'vat.detailed.tree'
    _description = "Vat Detail Tree"

    employee = fields.Many2one('hr.employee',string='Employee')
    percentage = fields.Float(string='Percentage')
    voucher = fields.Char(string='Voucher No')
    journal_entry = fields.Many2one('account.move','Invoices')
    commission = fields.Float(string='Inv/Bill Total')
    salesperson = fields.Many2one('res.users','Salesperson')
    arrival_date = fields.Date("Arrival Date")
    departure_date = fields.Date("Departure Date")
    hotel_ids = fields.Many2many('res.partner',string="Hotel")
    partner_id = fields.Many2one('res.partner',"Customer")
    financial_term = fields.Selection([
    ('pre_paid', 'Pre-Paid'),
    ('credit', 'Credit'),
    ], string="Financial Term",related='journal_entry.financial_term')
    invoice_payment_state = fields.Selection(selection=[
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid')],
        string='Payment', store=True, readonly=True, copy=False,
        )
    tree_link = fields.Many2one('vat.detailed')

class AccMoveCommissionExt(models.Model):
    _inherit='account.move'

    is_commissioned = fields.Boolean('Is Commissioned', default=False)

    def write(self, vals):
        if 'package_no' in vals and 'invoice_user_id' not in vals and vals.get('package_no'):
            pkg = self.env['reservation.order'].search([('name', '=', vals['package_no'])], limit=1)
            vals['invoice_user_id'] = pkg.user_id.id if pkg and pkg.user_id else False
        return super(AccMoveCommissionExt, self).write(vals)
    
    @api.model
    def create(self, vals):
        new_rec = super(AccMoveCommissionExt,self).create(vals)
        if new_rec.package_no:
            pkg = self.env['reservation.order'].search([('name','=',new_rec.package_no)], limit=1)
            if pkg:
                new_rec.invoice_user_id = pkg.user_id.id
        return new_rec


class SaleOrderInvoiceUserSync(models.Model):
    _inherit = 'reservation.order'

    def write(self, vals):
        res = super(SaleOrderInvoiceUserSync, self).write(vals)
        if 'user_id' in vals:
            for order in self:
                self.env['account.move'].search([('package_no', '=', order.name)]).write({
                    'invoice_user_id': order.user_id.id or False,
                })
        return res