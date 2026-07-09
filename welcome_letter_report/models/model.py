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



class welcome_letter_report(models.AbstractModel):
    _name = 'report.welcome_letter_report.flight_report_report'
    _description = "Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        record = self.env['all.services'].browse(docids)

        return {
            'doc_ids': docids,
            'doc_model':'all.services',
            'data': data,
            'docs': record,
        }