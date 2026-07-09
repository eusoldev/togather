# #-*- coding:utf-8 -*-

import os
import xlsxwriter
from io import BytesIO
from datetime import date
from datetime import date, timedelta
import datetime
import time
from odoo import api, models, fields
from odoo.exceptions import ValidationError, UserError
from odoo.tools import config
import base64
import string
import sys
from odoo import api, models, fields,_
from odoo.tools import config
import base64
import string
import sys
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, date
import calendar
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from operator import itemgetter


class Check_arrival_date(models.TransientModel):
    _name = "check.date.report"
    _description = 'Arriavl And Departure Report Wizard'
    form = fields.Date(string="From",required=True)
    to = fields.Date(string="To",required=True)
    company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company)
    print_excel = fields.Selection([
        ('excel', 'Excel Report'),
        ('pdf', 'PDF Report')], string='Report Type', help='Choose Report type', default='pdf')
   
    def generate_report(self):
        data = {}
        data['form'] = self.read(['form','to','company_id','print_excel'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['form','to','company_id','print_excel'])[0])
        if self.print_excel == 'pdf':
            return self.env.ref('check_arrival_date_report.report_check_arrival_date_report').report_action(self, data=data)
        if self.print_excel == 'excel':
            self.env.ref('check_arrival_date_report.report_check_arrival_date_report_xlsx').report_file = 'Arrival And Departure Date Report' + ' ' + str(fields.Date.today())
            return self.env.ref('check_arrival_date_report.report_check_arrival_date_report_xlsx').report_action(self, data=data)