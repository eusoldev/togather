# #-*- coding:utf-8 -*-

import os
import xlsxwriter
from io import BytesIO
from datetime import date
from datetime import date, timedelta
import datetime
import time
from odoo import api, models, fields
from odoo.tools import config
import base64
import string
import sys
from odoo import api, models, fields,_
from odoo.tools import config
import base64
import string
import sys
from datetime import datetime, timedelta, date
import calendar
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from operator import itemgetter


class SubClientReport(models.TransientModel):
    _name = "sub.client.report"
    _description = 'Sub Client Wizard'

    form = fields.Date(string="From",required=True)
    to = fields.Date(string="To",required=True)
    payment_status = fields.Selection([
        ('paid', 'Paid'),
        ('in_payment', 'Un-Paid'),
        ], string='Payment Status')
    typee = fields.Selection([
        ('all', 'All'),
        ('specific', 'Specific'),
        ], string='Type')
    partner_id = fields.Many2many('res.partner',string="Sub Agent",required=True)
    company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company)



    print_excel = fields.Selection([
        ('excel', 'Excel Report'),
        ('pdf', 'PDF Report')], string='Report Type', help='Choose Report type', default='pdf')

    date_range = fields.Selection(
        [('today', 'Today'),
         ('yesterday', 'Yesterday'),
         ('this_week', 'This Week'),
         ('next_week', 'Next Week'),
         ('last_week', 'Last Week'),
         ('this_month', 'This Month'),
         ('next_month', 'Next Month'),
         ('this_quarter', 'This Quarter'),
         ('next_quarter', 'Next Quarter'),
         ('last_month', 'Last Month'),
         ('last_quarter', 'Last Quarter'),
         ('this_financial_year', 'This financial Year'),
         ('last_financial_year', 'Last Financial Year'),
         ('next_financial_year', 'Next Financial Year'),
         ],string='Date Range')

    @api.onchange('date_range')
    def onchange_date_range(self):
        if self.date_range:
            date = datetime.today()
            if self.date_range == 'today':
                self.form = date.strftime("%Y-%m-%d")
                self.to = date.strftime("%Y-%m-%d")

            date = (datetime.now() + relativedelta(days=0))
            if self.date_range == 'this_week':
                day_today = date - timedelta(days=date.weekday())
                self.form = (day_today - timedelta(days=date.weekday())).strftime("%Y-%m-%d")
                self.to = (day_today + timedelta(days=6)).strftime("%Y-%m-%d")

            date = (datetime.now() + relativedelta(days=7))
            if self.date_range == 'next_week':
                day_today = date - timedelta(days=date.weekday())
                self.form = (day_today - timedelta(days=date.weekday())).strftime("%Y-%m-%d")
                self.to = (day_today + timedelta(days=6)).strftime("%Y-%m-%d")

            date = (datetime.now() + relativedelta(months=0))
            if self.date_range == 'this_month':
                self.form = datetime(date.year, date.month, 1).strftime("%Y-%m-%d")
                self.to = datetime(date.year, date.month, calendar.mdays[date.month]).strftime("%Y-%m-%d")


            #  date = (datetime.now() + relativedelta(months=1))
            # if self.date_range == 'next_month':
            #     self.form = datetime(date.year, date.month, 1).strftime("%Y-%m-%d")
            #     self.to = datetime(date.year, date.month, calendar.mdays[date.month]).strftime("%Y-%m-%d")

            # if self.date_range == 'next_month':
            #     self.form = datetime(date.year, date.month,).strftime("%Y-%m-%d")
            #     self.to = datetime(date.year, date.month, calendar.mdays[date.month]).strftime("%Y-%m-%d")
            if self.date_range == 'this_quarter':
                if int((date.month - 1) / 3) == 0:  # First quarter
                    self.form = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                    self.to = datetime(date.year, 3, calendar.mdays[3]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 1:  # Second quarter
                    self.form = datetime(date.year, 4, 1).strftime("%Y-%m-%d")
                    self.to = datetime(date.year, 6, calendar.mdays[6]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 2:  # Third quarter
                    self.form = datetime(date.year, 7, 1).strftime("%Y-%m-%d")
                    self.to = datetime(date.year, 9, calendar.mdays[9]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 3:  # Fourth quarter
                    self.form = datetime(date.year, 10, 1).strftime("%Y-%m-%d")
                    self.to = datetime(date.year, 12, calendar.mdays[12]).strftime("%Y-%m-%d")



            if self.date_range == 'next_quarter':

                if int((date.month - 1) / 3) == 0:  # First quarter
                    self.form = datetime(date.year, 4, 1).strftime("%Y-%m-%d")
                    self.to = datetime(date.year, 6, calendar.mdays[6]).strftime("%Y-%m-%d")


                if int((date.month - 1) / 3) == 1:  # Second quarter
                    self.form = datetime(date.year, 7, 1).strftime("%Y-%m-%d")
                    self.to = datetime(date.year, 9, calendar.mdays[9]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 2:  # Third quarter
                    self.form = datetime(date.year, 10, 1).strftime("%Y-%m-%d")
                    self.to = datetime(date.year, 12, calendar.mdays[12]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 3:  # Fourth quarter
                    self.form = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                    self.to = datetime(date.year, 3, calendar.mdays[3]).strftime("%Y-%m-%d")



            if self.date_range == 'this_financial_year':
                self.form = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                print("___________________")
                print(self.form)
                print("___________________")
                self.to = datetime(date.year, 12, 31).strftime("%Y-%m-%d")
                print("iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
                print(self.to)
                print("iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
            date = (datetime.now() - relativedelta(days=1))
            if self.date_range == 'yesterday':
                self.form = date.strftime("%Y-%m-%d")
                self.to = date.strftime("%Y-%m-%d")
            date = (datetime.now() - relativedelta(days=7))
            if self.date_range == 'last_week':
                day_today = date - timedelta(days=date.weekday())
                self.form = (day_today - timedelta(days=date.weekday())).strftime("%Y-%m-%d")
                self.to = (day_today + timedelta(days=6)).strftime("%Y-%m-%d")
            date = (datetime.now() - relativedelta(months=1))
            if self.date_range == 'last_month':
                self.form = datetime(date.year, date.month, 1).strftime("%Y-%m-%d")
                self.to = datetime(date.year, date.month, calendar.mdays[date.month]).strftime("%Y-%m-%d")

            date = (datetime.now() + relativedelta(months=1))
            if self.date_range == 'next_month':
                self.form = datetime(date.year, date.month, 1).strftime("%Y-%m-%d")
                self.to = datetime(date.year, date.month, calendar.mdays[date.month]).strftime("%Y-%m-%d")
            date = (datetime.now() - relativedelta(months=3))
            if self.date_range == 'last_quarter':
                if int((date.month - 1) / 3) == 0:  # First quarter
                    self.form = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                    self.to = datetime(date.year, 3, calendar.mdays[3]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 1:  # Second quarter
                    self.form = datetime(date.year, 4, 1).strftime("%Y-%m-%d")
                    self.to = datetime(date.year, 6, calendar.mdays[6]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 2:  # Third quarter
                    self.form = datetime(date.year, 7, 1).strftime("%Y-%m-%d")
                    self.to = datetime(date.year, 9, calendar.mdays[9]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 3:  # Fourth quarter
                    self.form = datetime(date.year, 10, 1).strftime("%Y-%m-%d")
                    self.to = datetime(date.year, 12, calendar.mdays[12]).strftime("%Y-%m-%d")
            date = (datetime.now() - relativedelta(years=1))
            if self.date_range == 'last_financial_year':
                self.form = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                self.to = datetime(date.year, 12, 31).strftime("%Y-%m-%d")

            date = (datetime.now() + relativedelta(years=1))
            if self.date_range == 'next_financial_year':
                self.form = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                self.to = datetime(date.year, 12, 31).strftime("%Y-%m-%d")



    

    
    # @api.multi
    def generate_report(self):
        data = {}
        data['form'] = self.read(['form','to','typee','partner_id','payment_status','company_id','print_excel'])[0]
        return self._print_report(data)




    def _print_report(self, data):
        data['form'].update(self.read(['form','to','typee','partner_id','payment_status','company_id','print_excel'])[0])
        if self.print_excel == 'pdf':
            return self.env.ref('sub_agent_report.report_for_sub_client_report').report_action(self, data=data)
        if self.print_excel == 'excel':
            self.env.ref('sub_agent_report.report_for_sub_client_report_excel').report_file = "Sub Client Report %s"%(fields.Date.today())
            return self.env.ref('sub_agent_report.report_for_sub_client_report_excel').report_action(self, data=data)
