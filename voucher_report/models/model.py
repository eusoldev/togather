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
import json
import urllib.parse
import urllib.request



class voucher_report(models.AbstractModel):
    _name = 'report.voucher_report.voucher_report_report'
    _description = "Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        record = self.env['reservation.order'].browse(docids)

        company = record[:1].company_id or self.env.company

        def get_url(hotel_id):
            url = "http://maps.google.com/maps?oi=map&q="
            if hotel_id:
                if hotel_id.company_type == 'company':
                    if hotel_id.name:
                        url += hotel_id.name.replace(' ','+')
                    if hotel_id.street_name:
                        url += hotel_id.street_name.replace(' ','+')
                    if hotel_id.street2:
                        url += hotel_id.street2.replace(' ','+')
                    if hotel_id.street_number:
                        url += hotel_id.street_number.replace(' ','+')
                    if hotel_id.street_number2:
                        url += hotel_id.street_number2.replace(' ','+')
                    if hotel_id.city:
                        url += '+'+hotel_id.city.replace(' ','+')
                    if hotel_id.state_id:
                        url += '+'+hotel_id.state_id.name.replace(' ','+')
                    if hotel_id.zip:
                        url += '+'+hotel_id.zip.replace(' ','+')
                    if hotel_id.country_id:
                        url += '+'+hotel_id.country_id.name.replace(' ','+')
                else:
                    if hotel_id.name:
                        url += hotel_id.name.replace(' ','+')
                    if hotel_id.ind_street:
                        url += hotel_id.ind_street.replace(' ','+')
                    if hotel_id.ind_street2:
                        url += hotel_id.ind_street2.replace(' ','+')
                    if hotel_id.ind_city:
                        url += '+'+hotel_id.ind_city.replace(' ','+')
                    if hotel_id.ind_state_id:
                        url += '+'+hotel_id.ind_state_id.name.replace(' ','+')
                    if hotel_id.ind_zip:
                        url += '+'+hotel_id.ind_zip.replace(' ','+')
                    if hotel_id.ind_country_id:
                        url += '+'+hotel_id.ind_country_id.name.replace(' ','+')
            return url

        customer_m2m = []
        # for x in record.hotel_pkg:
        customer_m2m.append(record.partner_id)
        for x in record.itinarnay_package:
            for y in x.customer_m2m:
                if y not in customer_m2m:
                    customer_m2m.append(y)

        def getRoomTypes(r_types):
            room_types = ""
            for rt in r_types:
                room_types += rt.name+", "
            if room_types:
                room_types = room_types[:-2]
            return room_types

        return {
            'doc_ids': docids,
            'doc_model':'reservation.order',
            'data': data,
            'docs': record,
            'getRoomTypes': getRoomTypes,
            'company': company,
            # 'translate_to_ar': translate_to_ar,
            'customer_m2m': customer_m2m,
            'get_url': get_url,
        }


# class hr_salary_rule_ext(models.Model):
#     _inherit = 'hr.salary.rule'

#     arabic_name = fields.Char(string="Arabic Name")    
