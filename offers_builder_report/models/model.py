#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved
# 
#    from num2words import num2words
#    import base64
#    import re
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api
import datetime
from datetime import date, datetime, timedelta
from datetime import date
import time
import calendar
from datetime import time
from dateutil.relativedelta import relativedelta
import datetime as dt



class offers_builder_report(models.AbstractModel):
    _name = 'report.offers_builder_report.offers_builder_report'
    _description = "Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        record = self.env['offers.builder'].browse(docids)
        company = self.env['res.company'].search([])
        night_3 = 0
        night_4 = 0
        night_5 = 0
        extra_adult = 0
        for x in record.offers_builder_tree:
            night_3 += x.night_3
            night_4 += x.night_4
            night_5 += x.night_5
            extra_adult += x.extra_adult


        return {
            'doc_ids': docids,
            'doc_model':'offers.builder',
            'data': data,
            'docs': record,
            'company': company,
            'night_3': night_3,
            'night_4': night_4,
            'night_5': night_5,
            'extra_adult': extra_adult,
        }
        