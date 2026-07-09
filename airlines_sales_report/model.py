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
from PIL import Image, ImageDraw




class airlines_sales_report(models.AbstractModel):
    _name = 'report.airlines_sales_report.airlines_sales_report'
    _description = 'Airline Sales Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        record_wizard = self.env['air.sales.report'].browse(self.env.context.get('active_ids'))
        form = record_wizard.form
        to = record_wizard.to
        company = record_wizard.company_id
        is_com = record_wizard.is_com
        partner_id = record_wizard.partner_id

        hotel = record_wizard.hotel

        country_id = record_wizard.country_id
        booking_type = record_wizard.booking_type
        
        if partner_id:
            partner = []
            for x in partner_id:
                partner.append(x)
        else:
            partner = self.env['hr.employee'].search([])

        main_list = []

        serial_total = 0

        for x in partner:

            if hotel:
                hotel_search = ('hotel_id','=',hotel.id)
            if not hotel:
                hotel_search = ('hotel_id','!=',False)


            if is_com =='is_c' and  booking_type =='arrival_date':
                    record = self.env['all.services'].search([('flights_return.arrival_date','>=',form),('flights_return.arrival_date','<=',to),('flights_return.user_id','=',x.user_id.id),('flights_return.stages','=','validate'),('flights_return.commissioned','=',True)])

            if is_com =='is_c' and  booking_type =='book_date':
                record = self.env['all.services'].search([('flights_return.date_order','>=',form),('flights_return.date_order','<=',to),('flights_return.user_id','=',x.user_id.id),('flights_return.stages','=','validate'),('flights_return.commissioned','=',True)])

            
            if is_com =='is_c' and  booking_type =='dep_date':
                record = self.env['all.services'].search([('flights_return.departure_date','>=',form),('flights_return.departure_date','<=',to),('flights_return.user_id','=',x.user_id.id),('flights_return.stages','=','validate'),('flights_return.commissioned','=',True)])

            if is_com =='is_not_c' and  booking_type =='arrival_date':
                record = self.env['all.services'].search([('flights_return.arrival_date','>=',form),('flights_return.arrival_date','<=',to),('flights_return.user_id','=',x.user_id.id),('flights_return.stages','=','validate'),('flights_return.commissioned','=',False)])
            
            if is_com =='is_not_c' and  booking_type =='dep_date':
                record = self.env['all.services'].search([('flights_return.departure_date','>=',form),('flights_return.departure_date','<=',to),('flights_return.user_id','=',x.user_id.id),('flights_return.stages','=','validate'),('flights_return.commissioned','=',False)])

            
            if is_com =='is_not_c' and  booking_type =='book_date':
                record = self.env['all.services'].search([('flights_return.date_order','>=',form),('flights_return.date_order','<=',to),('flights_return.user_id','=',x.user_id.id),('flights_return.stages','=','validate'),('flights_return.commissioned','=',False)])

            for inv in record:
               
                serial_total += 1

                room_type_list = []

                if country_id:
                    if country_id.id in inv.flights_return.destination.ids:
                        customer_m = []
                        for m in inv.customer_m2m:
                            customer_m.append(m.name)
                            
                        main_list.append({
                            'rq_number':inv.flights_return.name,
                            'sale_person':x.name,
                            'supplier':inv.supplier.name,
                            'customer':customer_m,
                            'form_loc':inv.from_loc.city,
                            'to_loc':inv.to_loc.city,
                            'e-ticket':inv.e_ticket,
                            'class':inv.fight_class.name,
                            'departure_date':inv.departures,
                            'return_date':inv.arrival,
                            'no_of_guest':inv.no_of_person,
                            'airline_pnr':inv.cc,
                            'net':inv.price,
                            'commission':inv.commission,
                            'total':inv.total,
                            })

                if not country_id:
                    customer_m = []
                    for m in inv.customer_m2m:
                        customer_m.append(m.name)
                    main_list.append({
                         'rq_number':inv.flights_return.name,
                            'sale_person':x.name,
                            'supplier':inv.supplier.name,
                            'customer':customer_m,
                            'form_loc':inv.from_loc.city,
                            'airline_pnr':inv.airline_pnr,
                            'to_loc':inv.to_loc.city,
                            'e-ticket':inv.e_ticket,
                            'class':inv.fight_class.name,
                            'departure_date':inv.departures,
                            'return_date':inv.arrival,
                            'no_of_guest':inv.no_of_person,
                            'net':inv.price,
                            'commission':inv.commission,
                            'total':inv.total,
                        })

        return {
            'doc_ids': docids,
            'doc_model':'all.services',
            'form': form,
            'to': to,
            'company': company,
            'main_list': main_list,
            'serial_total': serial_total,
        }
