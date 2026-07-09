from odoo import api, models, fields
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError
import datetime
from datetime import date
from datetime import date, timedelta
import datetime
from dateutil.relativedelta import *
import math
from PIL import Image, ImageDraw


class hotel_production_report(models.AbstractModel):
    _name = 'report.hotel_production_report.hotel_production_report'
    _description = 'Hotel Production Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        # self.model = self.env.context.get('active_model')
        # record_wizard = self.env[self.model].browse(self.env.context.get('active_id'))
        record_wizard = self.env['hotel.production.report'].browse(self.env.context.get('active_ids'))

        form = record_wizard.form
        to = record_wizard.to
        typee = record_wizard.typee
        partner_id = record_wizard.partner_id
        company = record_wizard.company_id
        report_type = record_wizard.report_type
        country_id = record_wizard.country_id
        booking_type = record_wizard.booking_type

        if typee == 'all':
            if report_type == 'vendor':
                partner = self.env['res.partner'].sudo().search([('hotel_supplier','=',True)])
            if report_type == 'hotel':
                partner = self.env['res.partner'].sudo().search([('hotel_supplier','=',True)])
            if report_type == 'destination':
                partner = self.env['destination.name'].sudo().search([])
        else:
            partner = []
            if report_type == 'hotel':
                for x in partner_id:
                    partner.append(x)

            if report_type == 'vendor':
                for x in partner_id:
                    partner.append(x)

            if report_type == 'destination':
                for x in country_id:

                    partner.append(x)
                    print("1111111111111111111111111")
                    print(partner)
                    print("1111111111111111111111111")
        all_part_selected = []
        all_part_selected_2 = []
        
        hotel_main_list = []
        hotel_summary_list = []

        for x in partner:
            all_part_selected.append([x.id])
            all_part_selected_2.append(x.id)
            if report_type == 'vendor':
                hot_dest = ('partner_id','=',x.id)
                record = self.env['account.move'].sudo().search([('date','>=',form),('date','<=',to),hot_dest,('state','=','posted'),('move_type','=','in_invoice')])

            # privous logic
            # if report_type == 'destination':
            #     hot_dest = ('partner_id.country_id','=',x.id)
            #     record = self.env['account.move'].sudo().search([('date','>=',form),('date','<=',to),hot_dest,('state','=','posted'),('move_type','=','in_invoice')])

            if report_type == 'destination':
                dest_sales = self.env['reservation.order'].sudo().search([
                    ('destination', 'in', x.ids)
                ])
                sale_names = dest_sales.mapped('name')

                record = self.env['account.move'].sudo().search([
                    ('date','>=', form),
                    ('date','<=', to),
                    ('state','=', 'posted'),
                    ('move_type','=', 'in_invoice'),
                    ('invoice_origin', 'in', sale_names),     # sale order destination
                ])


            if report_type == 'hotel':
                # all_sales_services = self.env['all.services'].sudo().search([('product_id','=',2),('hotel_id', '=',x.id)])
                all_sales_services = self.env['reservation.order'].sudo().search([('hotel_pkg.hotel_id', '=', x.id)])

                pkgs_list = []
                for pkg in all_sales_services:
                    if pkg.name not in pkgs_list:
                        pkgs_list.append(pkg.name)
                # for service in all_sales_services:
                #   if service.hotel_return.stages == 'validate':
                #       if service.hotel_return.name not in pkgs_list:
                #           pkgs_list.append(service.hotel_return.name)

                record = self.env['account.move'].sudo().search([('date','>=',form),('date','<=',to),('invoice_origin','in',pkgs_list),('state','=','posted'),('move_type','=','in_invoice'),('hotel_ids','!=',False)])


            main_list = []
            pkg_total = 0
            serial_total = 0
            for inv in record:
                if report_type == 'hotel':
                    if inv.hotel_ids.ids in all_part_selected:
                        for gi in inv.hotel_ids:
                            if gi.id == x.id:
                                serial_total += 1
                else:
                    serial_total += 1

                package = self.env['reservation.order'].sudo().search([('name','=',inv.invoice_origin)])
                date_from = ""
                date_to = ""
                currency = ""
                nights = 0
                amnt_fc = 0
                currency_fc=0
                same_suppliers=0
                for hotel in package.hotel_pkg:

                    if booking_type =='arrival_date':
                            if hotel.hotel_return.arrival_date >= form and hotel.hotel_return.arrival_date <= to: 
                                if report_type == 'hotel':
                                    if x.id in inv.hotel_ids.ids and hotel.hotel_id.id == x.id:

                                        for final in inv.hotel_ids:

                                            # ensure this loop is processing the correct hotel
                                            if final.id != x.id:
                                                continue

                                            date_from = ""
                                            date_to = ""
                                            currency = ""
                                            nights = 0
                                            amnt_fc = 0
                                            currency_fc = 0

                                            # Match supplier with vendor bill supplier
                                            if hotel.supplier and hotel.supplier.id == inv.partner_id.id:

                                                same_suppliers += 1

                                                # CUSTOMER LIST
                                                customer_name = []
                                                if hotel.customer_m2m:
                                                    for y in hotel.customer_m2m:
                                                        customer_name.append(y.name)

                                                # ROOM TYPES
                                                room_type_list = []
                                                for t in hotel.room_type:
                                                    room_type_list.append(t.name)

                                                # NIGHTS
                                                amnt_fc += hotel.amnt_fc
                                                nights += hotel.nights * hotel.room_qty

                                                # DATE FROM
                                                if not date_from:
                                                    date_from = hotel.date_from
                                                else:
                                                    date_from = str(date_from) + "/" + str(hotel.date_from)

                                                # DATE TO
                                                if not date_to:
                                                    date_to = hotel.date_to
                                                else:
                                                    date_to = str(date_to) + "/" + str(hotel.date_to)

                                                # CURRENCY
                                                if not currency:
                                                    currency = hotel.currency_name.name
                                                else:
                                                    currency = str(currency) + "/" + str(hotel.currency_name.name)

                                                # HOTEL NAME IN REPORT
                                                if report_type == 'hotel':
                                                    all_hotels = []
                                                    for ah in inv.hotel_ids:
                                                        if ah.id == x.id:
                                                            all_hotels.append(ah.name)
                                                    Hotel_name = all_hotels

                                                elif report_type == 'vendor':
                                                    Hotel_name = inv.partner_id.name

                                                elif report_type == 'destination':
                                                    Hotel_name = inv.partner_id.country_id.name

                                                # --- ADD FINAL RECORD IN MAIN LIST ---
                                                main_list.append({
                                                    'Invoice_no': inv.name,
                                                    'date_order': hotel.hotel_return.date_order,
                                                    'arrival_date': hotel.hotel_return.arrival_date,
                                                    'customer_name': customer_name,
                                                    'room_type': room_type_list,
                                                    'no_of_guest': hotel.no_of_person,
                                                    'rq_number': inv.package_no,
                                                    'Hotel_name': Hotel_name,
                                                    'check_in': date_from,
                                                    'check_out': date_to,
                                                    'nights': nights,
                                                    'amount_fc': amnt_fc,
                                                    'currency_id': currency,
                                                    'toatal_pkage_amount': inv.amount_total,
                                                    'creation_date': package.create_date,
                                                    'sale_person': package.user_id.name,
                                                    'status': dict(inv._fields['payment_state'].selection).get(inv.payment_state),
                                                })

                                                # Summaries
                                                if same_suppliers == 1:
                                                    pkg_total += inv.amount_total

                                else:
                                    date_from = ""
                                    date_to = ""
                                    currency = ""
                                    nights = 0
                                    amnt_fc = 0
                                    currency_fc=0
                                    if hotel.supplier:
                                        if hotel.supplier.id == inv.partner_id.id:
                                            same_suppliers+=1
                                            customer_name = []
                                            room_type_list = []
                                            for t in hotel.room_type:
                                                room_type_list.append(t.name)

                                            if hotel.customer_m2m:
                                                for y in hotel.customer_m2m:
                                                    customer_name.append(y.name)


                                            amnt_fc += hotel.amnt_fc
                                            nights += hotel.nights*hotel.room_qty
                                            if not date_from:
                                                date_from = hotel.date_from
                                            else:
                                                date_from = str(date_from)+"/"+str(hotel.date_from)
                                            if not date_to:
                                                date_to = hotel.date_to
                                            else:
                                                date_to = str(date_to)+"/"+str(hotel.date_to)
                                            if not currency:
                                                currency = hotel.currency_name.name
                                            else:
                                                currency = str(currency)+"/"+str(hotel.currency_name.name)

                                            if inv.amount_total:
                                                if report_type == 'hotel':
                                                    all_hotels = []
                                                    for ah in inv.hotel_ids:
                                                        if ah.id == x.id:
                                                            all_hotels.append(ah.name)

                                                    Hotel_name = all_hotels
                                                if report_type == 'vendor':
                                                    Hotel_name = inv.partner_id.name
                                                if report_type == 'destination':
                                                    Hotel_name = ''
                                                    selected_dest_ids = country_id.ids  # wizard se selected destinations

                                                    for rec in hotel.hotel_return:
                                                        for des in rec.destination:
                                                            if des.id in selected_dest_ids:
                                                                Hotel_name = des.name
                                                                break

                                                main_list.append({
                                                    'Invoice_no':inv.name,
                                                    'date_order':hotel.hotel_return.date_order,
                                                    'arrival_date':hotel.hotel_return.arrival_date,
                                                    'customer_name':customer_name,
                                                    'room_type':room_type_list,
                                                    'no_of_guest':hotel.no_of_person,
                                                    'rq_number':inv.package_no,
                                                    'Hotel_name':Hotel_name,
                                                    'get_Hotel_name':hotel.hotel_id.name,
                                                    'check_in':date_from,
                                                    'check_out':date_to,
                                                    'nights':nights,
                                                    'amount_fc':amnt_fc,
                                                    'currency_id':currency,
                                                    'toatal_pkage_amount':inv.amount_total,
                                                    'creation_date':package.create_date,
                                                    'sale_person':package.user_id.name,
                                                    'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
                                                    })
                                                if same_suppliers==1:
                                                    pkg_total += inv.amount_total

                    if booking_type =='book_date':
                            
                            if hotel.hotel_return.date_order.date() >= form and hotel.hotel_return.date_order.date() <= to: 

                                if report_type == 'hotel':
                                    if inv.hotel_ids.ids in all_part_selected and hotel.hotel_id.id in all_part_selected_2:
                                        for final in inv.hotel_ids:
                                            date_from = ""
                                            date_to = ""
                                            currency = ""
                                            nights = 0
                                            amnt_fc = 0
                                            currency_fc=0
                                            if final.id == hotel.hotel_id.id and final.id == x.id and hotel.hotel_id.id ==x.id:
                                                if hotel.supplier:
                                                    if hotel.supplier.id == inv.partner_id.id:
                                                        same_suppliers+=1
                                                        customer_name = []
                                                        room_type_list = []
                                                        for t in hotel.room_type:
                                                            room_type_list.append(t.name)

                                                        if hotel.customer_m2m:
                                                            for y in hotel.customer_m2m:
                                                                customer_name.append(y.name)

                                                        amnt_fc += hotel.amnt_fc
                                                        nights += hotel.nights*hotel.room_qty
                                                        if not date_from:
                                                            date_from = hotel.date_from
                                                        else:
                                                            date_from = str(date_from)+"/"+str(hotel.date_from)
                                                        if not date_to:
                                                            date_to = hotel.date_to
                                                        else:
                                                            date_to = str(date_to)+"/"+str(hotel.date_to)
                                                        if not currency:
                                                            currency = hotel.currency_name.name
                                                        else:
                                                            currency = str(currency)+"/"+str(hotel.currency_name.name)

                                                        if inv.amount_total:
                                                            if report_type == 'hotel':
                                                                all_hotels = []
                                                                for ah in inv.hotel_ids:
                                                                    if ah.id == x.id:
                                                                        all_hotels.append(ah.name)

                                                                Hotel_name = all_hotels
                                                            if report_type == 'vendor':
                                                                Hotel_name = inv.partner_id.name
                                                            if report_type == 'destination':
                                                                Hotel_name = inv.partner_id.country_id.name


                                                            main_list.append({
                                                                'Invoice_no':inv.name,
                                                                'date_order':hotel.hotel_return.date_order,
                                                                'arrival_date':hotel.hotel_return.arrival_date,
                                                                'customer_name':customer_name,
                                                                'room_type':room_type_list,
                                                                'no_of_guest':hotel.no_of_person,
                                                                'rq_number':inv.package_no,
                                                                'Hotel_name':Hotel_name,
                                                                'check_in':date_from,
                                                                'check_out':date_to,
                                                                'nights':nights,
                                                                'amount_fc':amnt_fc,
                                                                'currency_id':currency,
                                                                'toatal_pkage_amount':inv.amount_total,
                                                                'creation_date':package.create_date,
                                                                'sale_person':package.user_id.name,
                                                                'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
                                                                })
                                                            if same_suppliers == 1:
                                                                pkg_total += inv.amount_total
                                else:
                                    date_from = ""
                                    date_to = ""
                                    currency = ""
                                    nights = 0
                                    amnt_fc = 0
                                    currency_fc=0
                                    if hotel.supplier:
                                        if hotel.supplier.id == inv.partner_id.id:
                                            same_suppliers+=1
                                            customer_name = []
                                            room_type_list = []
                                            for t in hotel.room_type:
                                                room_type_list.append(t.name)

                                            if hotel.customer_m2m:
                                                for y in hotel.customer_m2m:
                                                    customer_name.append(y.name)


                                            amnt_fc += hotel.amnt_fc
                                            nights += hotel.nights*hotel.room_qty
                                            if not date_from:
                                                date_from = hotel.date_from
                                            else:
                                                date_from = str(date_from)+"/"+str(hotel.date_from)
                                            if not date_to:
                                                date_to = hotel.date_to
                                            else:
                                                date_to = str(date_to)+"/"+str(hotel.date_to)
                                            if not currency:
                                                currency = hotel.currency_name.name
                                            else:
                                                currency = str(currency)+"/"+str(hotel.currency_name.name)

                                            if inv.amount_total:
                                                if report_type == 'hotel':
                                                    all_hotels = []
                                                    for ah in inv.hotel_ids:
                                                        if ah.id == x.id:
                                                            all_hotels.append(ah.name)

                                                    Hotel_name = all_hotels
                                                if report_type == 'vendor':
                                                    Hotel_name = inv.partner_id.name
                                                if report_type == 'destination':
                                                    Hotel_name = ''
                                                    selected_dest_ids = country_id.ids  # wizard se selected destinations

                                                    for rec in hotel.hotel_return:
                                                        for des in rec.destination:
                                                            if des.id in selected_dest_ids:
                                                                Hotel_name = des.name
                                                                break


                                                main_list.append({
                                                    'Invoice_no':inv.name,
                                                    'date_order':hotel.hotel_return.date_order,
                                                    'arrival_date':hotel.hotel_return.arrival_date,
                                                    'customer_name':customer_name,
                                                    'room_type':room_type_list,
                                                    'get_Hotel_name':hotel.hotel_id.name,
                                                    'no_of_guest':hotel.no_of_person,
                                                    'rq_number':inv.package_no,
                                                    'Hotel_name':Hotel_name,
                                                    'check_in':date_from,
                                                    'check_out':date_to,
                                                    'nights':nights,
                                                    'amount_fc':amnt_fc,
                                                    'currency_id':currency,
                                                    'toatal_pkage_amount':inv.amount_total,
                                                    'creation_date':package.create_date,
                                                    'sale_person':package.user_id.name,
                                                    'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
                                                    })
                                                if same_suppliers ==1:
                                                    pkg_total += inv.amount_total

                    if booking_type !='book_date' and booking_type !='arrival_date' :
                        if report_type == 'hotel':
                            if inv.hotel_ids.ids in all_part_selected and hotel.hotel_id.id in all_part_selected_2:
                                for final in inv.hotel_ids:
                                    date_from = ""
                                    date_to = ""
                                    currency = ""
                                    nights = 0
                                    amnt_fc = 0
                                    currency_fc=0
                                    if final.id == hotel.hotel_id.id and final.id == x.id and hotel.hotel_id.id ==x.id:
                                        if hotel.supplier:
                                            if hotel.supplier.id == inv.partner_id.id:
                                                same_suppliers+=1
                                                customer_name = []
                                                room_type_list = []
                                                for t in hotel.room_type:
                                                    room_type_list.append(t.name)

                                                if hotel.customer_m2m:
                                                    for y in hotel.customer_m2m:
                                                        customer_name.append(y.name)

                                                amnt_fc += hotel.amnt_fc
                                                nights += hotel.nights*hotel.room_qty
                                                if not date_from:
                                                    date_from = hotel.date_from
                                                else:
                                                    date_from = str(date_from)+"/"+str(hotel.date_from)
                                                if not date_to:
                                                    date_to = hotel.date_to
                                                else:
                                                    date_to = str(date_to)+"/"+str(hotel.date_to)
                                                if not currency:
                                                    currency = hotel.currency_name.name
                                                else:
                                                    currency = str(currency)+"/"+str(hotel.currency_name.name)

                                                if inv.amount_total:
                                                    if report_type == 'hotel':
                                                        all_hotels = []
                                                        for ah in inv.hotel_ids:
                                                            if ah.id == x.id:
                                                                all_hotels.append(ah.name)

                                                        Hotel_name = all_hotels
                                                    if report_type == 'vendor':
                                                        Hotel_name = inv.partner_id.name
                                                    if report_type == 'destination':
                                                        Hotel_name = inv.partner_id.country_id.name

                                                    main_list.append({
                                                        'Invoice_no':inv.name,
                                                        'date_order':hotel.hotel_return.date_order,
                                                        'arrival_date':hotel.hotel_return.arrival_date,
                                                        'customer_name':customer_name,
                                                        'room_type':room_type_list,
                                                        'no_of_guest':hotel.no_of_person,
                                                        'rq_number':inv.package_no,
                                                        'Hotel_name':Hotel_name,
                                                        'check_in':date_from,
                                                        'check_out':date_to,
                                                        'nights':nights,
                                                        'amount_fc':amnt_fc,
                                                        'currency_id':currency,
                                                        'toatal_pkage_amount':inv.amount_total,
                                                        'creation_date':package.create_date,
                                                        'sale_person':package.user_id.name,
                                                        'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
                                                        })
                                                    if same_suppliers==1:
                                                        pkg_total += inv.amount_total
                        else:
                            date_from = ""
                            date_to = ""
                            currency = ""
                            nights = 0
                            amnt_fc = 0
                            currency_fc=0
                            if hotel.supplier:
                                if hotel.supplier.id == inv.partner_id.id:
                                    same_suppliers+=1
                                    customer_name = []
                                    room_type_list = []
                                    for t in hotel.room_type:
                                        room_type_list.append(t.name)

                                    if hotel.customer_m2m:
                                        for y in hotel.customer_m2m:
                                            customer_name.append(y.name)

                                    amnt_fc += hotel.amnt_fc
                                    nights += hotel.nights*hotel.room_qty
                                    if not date_from:
                                        date_from = hotel.date_from
                                    else:
                                        date_from = str(date_from)+"/"+str(hotel.date_from)
                                    if not date_to:
                                        date_to = hotel.date_to
                                    else:
                                        date_to = str(date_to)+"/"+str(hotel.date_to)
                                    if not currency:
                                        currency = hotel.currency_name.name
                                    else:
                                        currency = str(currency)+"/"+str(hotel.currency_name.name)

                                    if inv.amount_total:
                                        if report_type == 'hotel':
                                            all_hotels = []
                                            for ah in inv.hotel_ids:
                                                if ah.id == x.id:
                                                    all_hotels.append(ah.name)

                                            Hotel_name = all_hotels
                                        if report_type == 'vendor':
                                            Hotel_name = inv.partner_id.name
                                        if report_type == 'destination':
                                            Hotel_name = ''
                                            selected_dest_ids = country_id.ids  # wizard se selected destinations

                                            for rec in hotel.hotel_return:
                                                for des in rec.destination:
                                                    if des.id in selected_dest_ids:
                                                        Hotel_name = des.name
                                                        break

                                        main_list.append({
                                            'Invoice_no':inv.name,
                                            'date_order':hotel.hotel_return.date_order,
                                            'arrival_date':hotel.hotel_return.arrival_date,
                                            'customer_name':customer_name,
                                            'room_type':room_type_list,
                                            'get_Hotel_name':hotel.hotel_id.name,
                                            'no_of_guest':hotel.no_of_person,
                                            'rq_number':inv.package_no,
                                            'Hotel_name':Hotel_name,
                                            'check_in':date_from,
                                            'check_out':date_to,
                                            'nights':nights,
                                            'amount_fc':amnt_fc,
                                            'currency_id':currency,
                                            'toatal_pkage_amount':inv.amount_total,
                                            'creation_date':package.create_date,
                                            'sale_person':package.user_id.name,
                                            'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
                                            })
                                        if same_suppliers==1:
                                            pkg_total += inv.amount_total


            if pkg_total > 0:
                hotel_summary_list.append({
                    'hotel_name':x.name,
                    'pkg_total':pkg_total,
                    })

            if main_list:
                hotel_main_list.append({
                    'hotel':x.name,
                    'serial_total':serial_total,
                    'main_list':main_list,
                    'pkg_total':pkg_total,
                    })



        return {
            'doc_ids': docids,
            'doc_model':'account.move',
            'form': form,
            'to': to,
            'report_type': report_type,
            'company': company,
            'hotel_main_list': hotel_main_list,
            'hotel_summary_list': hotel_summary_list,
        }




class hotel_production_report_xlsx(models.AbstractModel):
    _name = 'report.hotel_production_report.hotel_production_report_xlsx'

    _inherit = 'report.report_xlsx.abstract'
    _description="Hotel Production Report"





    def generate_xlsx_report(self, workbook, data, wizard_obj):



        # self.model = self.env.context.get('active_model')
        # record_wizard = self.env[self.model].browse(self.env.context.get('active_id'))
        record_wizard = self.env['hotel.production.report'].browse(self.env.context.get('active_ids'))

        form = record_wizard.form
        to = record_wizard.to
        typee = record_wizard.typee
        partner_id = record_wizard.partner_id
        company = record_wizard.company_id
        report_type = record_wizard.report_type
        country_id = record_wizard.country_id
        booking_type = record_wizard.booking_type

        if typee == 'all':
            if report_type == 'vendor':
                partner = self.env['res.partner'].sudo().search([('hotel_supplier','=',True)])
            if report_type == 'hotel':
                partner = self.env['res.partner'].sudo().search([('hotel_supplier','=',True)])
            if report_type == 'destination':
                partner = self.env['destination.name'].sudo().search([])
        else:
            partner = []
            if report_type == 'hotel':
                for x in partner_id:
                    partner.append(x)

            if report_type == 'vendor':
                for x in partner_id:
                    partner.append(x)

            if report_type == 'destination':
                for x in country_id:

                    partner.append(x)
                    print("1111111111111111111111111")
                    print(partner)
                    print("1111111111111111111111111")
        all_part_selected = []
        all_part_selected_2 = []
        
        hotel_main_list = []
        hotel_summary_list = []

        for x in partner:
            all_part_selected.append([x.id])
            all_part_selected_2.append(x.id)
            if report_type == 'vendor':
                hot_dest = ('partner_id','=',x.id)
                record = self.env['account.move'].sudo().search([('date','>=',form),('date','<=',to),hot_dest,('state','=','posted'),('move_type','=','in_invoice')])

            # privous logic
            # if report_type == 'destination':
            #     hot_dest = ('partner_id.country_id','=',x.id)
            #     record = self.env['account.move'].sudo().search([('date','>=',form),('date','<=',to),hot_dest,('state','=','posted'),('move_type','=','in_invoice')])

            if report_type == 'destination':
                dest_sales = self.env['reservation.order'].sudo().search([
                    ('destination', 'in', x.ids)
                ])
                sale_names = dest_sales.mapped('name')

                record = self.env['account.move'].sudo().search([
                    ('date','>=', form),
                    ('date','<=', to),
                    ('state','=', 'posted'),
                    ('move_type','=', 'in_invoice'),
                    ('invoice_origin', 'in', sale_names),     # sale order destination
                ])


            if report_type == 'hotel':
                # all_sales_services = self.env['all.services'].sudo().search([('product_id','=',2),('hotel_id', '=',x.id)])
                all_sales_services = self.env['reservation.order'].sudo().search([('hotel_pkg.hotel_id', '=', x.id)])

                pkgs_list = []
                for pkg in all_sales_services:
                    if pkg.name not in pkgs_list:
                        pkgs_list.append(pkg.name)
                # for service in all_sales_services:
                #   if service.hotel_return.stages == 'validate':
                #       if service.hotel_return.name not in pkgs_list:
                #           pkgs_list.append(service.hotel_return.name)

                record = self.env['account.move'].sudo().search([('date','>=',form),('date','<=',to),('invoice_origin','in',pkgs_list),('state','=','posted'),('move_type','=','in_invoice'),('hotel_ids','!=',False)])


            main_list = []
            pkg_total = 0
            serial_total = 0
            for inv in record:
                if report_type == 'hotel':
                    if inv.hotel_ids.ids in all_part_selected:
                        for gi in inv.hotel_ids:
                            if gi.id == x.id:
                                serial_total += 1
                else:
                    serial_total += 1

                package = self.env['reservation.order'].sudo().search([('name','=',inv.invoice_origin)])
                date_from = ""
                date_to = ""
                currency = ""
                nights = 0
                amnt_fc = 0
                currency_fc=0
                same_suppliers=0
                for hotel in package.hotel_pkg:

                    if booking_type =='arrival_date':
                            if hotel.hotel_return.arrival_date >= form and hotel.hotel_return.arrival_date <= to: 
                                if report_type == 'hotel':
                                    if x.id in inv.hotel_ids.ids and hotel.hotel_id.id == x.id:

                                        for final in inv.hotel_ids:

                                            # ensure this loop is processing the correct hotel
                                            if final.id != x.id:
                                                continue

                                            date_from = ""
                                            date_to = ""
                                            currency = ""
                                            nights = 0
                                            amnt_fc = 0
                                            currency_fc = 0

                                            # Match supplier with vendor bill supplier
                                            if hotel.supplier and hotel.supplier.id == inv.partner_id.id:

                                                same_suppliers += 1

                                                # CUSTOMER LIST
                                                customer_name = []
                                                if hotel.customer_m2m:
                                                    for y in hotel.customer_m2m:
                                                        customer_name.append(y.name)

                                                # ROOM TYPES
                                                room_type_list = []
                                                for t in hotel.room_type:
                                                    room_type_list.append(t.name)

                                                # NIGHTS
                                                amnt_fc += hotel.amnt_fc
                                                nights += hotel.nights * hotel.room_qty

                                                # DATE FROM
                                                if not date_from:
                                                    date_from = hotel.date_from
                                                else:
                                                    date_from = str(date_from) + "/" + str(hotel.date_from)

                                                # DATE TO
                                                if not date_to:
                                                    date_to = hotel.date_to
                                                else:
                                                    date_to = str(date_to) + "/" + str(hotel.date_to)

                                                # CURRENCY
                                                if not currency:
                                                    currency = hotel.currency_name.name
                                                else:
                                                    currency = str(currency) + "/" + str(hotel.currency_name.name)

                                                # HOTEL NAME IN REPORT
                                                if report_type == 'hotel':
                                                    all_hotels = []
                                                    for ah in inv.hotel_ids:
                                                        if ah.id == x.id:
                                                            all_hotels.append(ah.name)
                                                    Hotel_name = all_hotels

                                                elif report_type == 'vendor':
                                                    Hotel_name = inv.partner_id.name

                                                elif report_type == 'destination':
                                                    Hotel_name = inv.partner_id.country_id.name

                                                # --- ADD FINAL RECORD IN MAIN LIST ---
                                                main_list.append({
                                                    'Invoice_no': inv.name,
                                                    'date_order': hotel.hotel_return.date_order,
                                                    'arrival_date': hotel.hotel_return.arrival_date,
                                                    'customer_name': customer_name,
                                                    'room_type': room_type_list,
                                                    'no_of_guest': hotel.no_of_person,
                                                    'rq_number': inv.package_no,
                                                    'Hotel_name': Hotel_name,
                                                    'check_in': date_from,
                                                    'check_out': date_to,
                                                    'nights': nights,
                                                    'amount_fc': amnt_fc,
                                                    'currency_id': currency,
                                                    'toatal_pkage_amount': inv.amount_total,
                                                    'creation_date': package.create_date,
                                                    'sale_person': package.user_id.name,
                                                    'status': dict(inv._fields['payment_state'].selection).get(inv.payment_state),
                                                })

                                                # Summaries
                                                if same_suppliers == 1:
                                                    pkg_total += inv.amount_total

                                else:
                                    date_from = ""
                                    date_to = ""
                                    currency = ""
                                    nights = 0
                                    amnt_fc = 0
                                    currency_fc=0
                                    if hotel.supplier:
                                        if hotel.supplier.id == inv.partner_id.id:
                                            same_suppliers+=1
                                            customer_name = []
                                            room_type_list = []
                                            for t in hotel.room_type:
                                                room_type_list.append(t.name)

                                            if hotel.customer_m2m:
                                                for y in hotel.customer_m2m:
                                                    customer_name.append(y.name)


                                            amnt_fc += hotel.amnt_fc
                                            nights += hotel.nights*hotel.room_qty
                                            if not date_from:
                                                date_from = hotel.date_from
                                            else:
                                                date_from = str(date_from)+"/"+str(hotel.date_from)
                                            if not date_to:
                                                date_to = hotel.date_to
                                            else:
                                                date_to = str(date_to)+"/"+str(hotel.date_to)
                                            if not currency:
                                                currency = hotel.currency_name.name
                                            else:
                                                currency = str(currency)+"/"+str(hotel.currency_name.name)

                                            if inv.amount_total:
                                                if report_type == 'hotel':
                                                    all_hotels = []
                                                    for ah in inv.hotel_ids:
                                                        if ah.id == x.id:
                                                            all_hotels.append(ah.name)

                                                    Hotel_name = all_hotels
                                                if report_type == 'vendor':
                                                    Hotel_name = inv.partner_id.name
                                                if report_type == 'destination':
                                                    Hotel_name = ''
                                                    selected_dest_ids = country_id.ids  # wizard se selected destinations

                                                    for rec in hotel.hotel_return:
                                                        for des in rec.destination:
                                                            if des.id in selected_dest_ids:
                                                                Hotel_name = des.name
                                                                break

                                                main_list.append({
                                                    'Invoice_no':inv.name,
                                                    'date_order':hotel.hotel_return.date_order,
                                                    'arrival_date':hotel.hotel_return.arrival_date,
                                                    'customer_name':customer_name,
                                                    'room_type':room_type_list,
                                                    'no_of_guest':hotel.no_of_person,
                                                    'rq_number':inv.package_no,
                                                    'Hotel_name':Hotel_name,
                                                    'get_Hotel_name':hotel.hotel_id.name,
                                                    'check_in':date_from,
                                                    'check_out':date_to,
                                                    'nights':nights,
                                                    'amount_fc':amnt_fc,
                                                    'currency_id':currency,
                                                    'toatal_pkage_amount':inv.amount_total,
                                                    'creation_date':package.create_date,
                                                    'sale_person':package.user_id.name,
                                                    'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
                                                    })
                                                if same_suppliers==1:
                                                    pkg_total += inv.amount_total

                    if booking_type =='book_date':
                            
                            if hotel.hotel_return.date_order.date() >= form and hotel.hotel_return.date_order.date() <= to: 

                                if report_type == 'hotel':
                                    if inv.hotel_ids.ids in all_part_selected and hotel.hotel_id.id in all_part_selected_2:
                                        for final in inv.hotel_ids:
                                            date_from = ""
                                            date_to = ""
                                            currency = ""
                                            nights = 0
                                            amnt_fc = 0
                                            currency_fc=0
                                            if final.id == hotel.hotel_id.id and final.id == x.id and hotel.hotel_id.id ==x.id:
                                                if hotel.supplier:
                                                    if hotel.supplier.id == inv.partner_id.id:
                                                        same_suppliers+=1
                                                        customer_name = []
                                                        room_type_list = []
                                                        for t in hotel.room_type:
                                                            room_type_list.append(t.name)

                                                        if hotel.customer_m2m:
                                                            for y in hotel.customer_m2m:
                                                                customer_name.append(y.name)

                                                        amnt_fc += hotel.amnt_fc
                                                        nights += hotel.nights*hotel.room_qty
                                                        if not date_from:
                                                            date_from = hotel.date_from
                                                        else:
                                                            date_from = str(date_from)+"/"+str(hotel.date_from)
                                                        if not date_to:
                                                            date_to = hotel.date_to
                                                        else:
                                                            date_to = str(date_to)+"/"+str(hotel.date_to)
                                                        if not currency:
                                                            currency = hotel.currency_name.name
                                                        else:
                                                            currency = str(currency)+"/"+str(hotel.currency_name.name)

                                                        if inv.amount_total:
                                                            if report_type == 'hotel':
                                                                all_hotels = []
                                                                for ah in inv.hotel_ids:
                                                                    if ah.id == x.id:
                                                                        all_hotels.append(ah.name)

                                                                Hotel_name = all_hotels
                                                            if report_type == 'vendor':
                                                                Hotel_name = inv.partner_id.name
                                                            if report_type == 'destination':
                                                                Hotel_name = inv.partner_id.country_id.name


                                                            main_list.append({
                                                                'Invoice_no':inv.name,
                                                                'date_order':hotel.hotel_return.date_order,
                                                                'arrival_date':hotel.hotel_return.arrival_date,
                                                                'customer_name':customer_name,
                                                                'room_type':room_type_list,
                                                                'no_of_guest':hotel.no_of_person,
                                                                'rq_number':inv.package_no,
                                                                'Hotel_name':Hotel_name,
                                                                'check_in':date_from,
                                                                'check_out':date_to,
                                                                'nights':nights,
                                                                'amount_fc':amnt_fc,
                                                                'currency_id':currency,
                                                                'toatal_pkage_amount':inv.amount_total,
                                                                'creation_date':package.create_date,
                                                                'sale_person':package.user_id.name,
                                                                'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
                                                                })
                                                            if same_suppliers == 1:
                                                                pkg_total += inv.amount_total
                                else:
                                    date_from = ""
                                    date_to = ""
                                    currency = ""
                                    nights = 0
                                    amnt_fc = 0
                                    currency_fc=0
                                    if hotel.supplier:
                                        if hotel.supplier.id == inv.partner_id.id:
                                            same_suppliers+=1
                                            customer_name = []
                                            room_type_list = []
                                            for t in hotel.room_type:
                                                room_type_list.append(t.name)

                                            if hotel.customer_m2m:
                                                for y in hotel.customer_m2m:
                                                    customer_name.append(y.name)


                                            amnt_fc += hotel.amnt_fc
                                            nights += hotel.nights*hotel.room_qty
                                            if not date_from:
                                                date_from = hotel.date_from
                                            else:
                                                date_from = str(date_from)+"/"+str(hotel.date_from)
                                            if not date_to:
                                                date_to = hotel.date_to
                                            else:
                                                date_to = str(date_to)+"/"+str(hotel.date_to)
                                            if not currency:
                                                currency = hotel.currency_name.name
                                            else:
                                                currency = str(currency)+"/"+str(hotel.currency_name.name)

                                            if inv.amount_total:
                                                if report_type == 'hotel':
                                                    all_hotels = []
                                                    for ah in inv.hotel_ids:
                                                        if ah.id == x.id:
                                                            all_hotels.append(ah.name)

                                                    Hotel_name = all_hotels
                                                if report_type == 'vendor':
                                                    Hotel_name = inv.partner_id.name
                                                if report_type == 'destination':
                                                    Hotel_name = ''
                                                    selected_dest_ids = country_id.ids  # wizard se selected destinations

                                                    for rec in hotel.hotel_return:
                                                        for des in rec.destination:
                                                            if des.id in selected_dest_ids:
                                                                Hotel_name = des.name
                                                                break


                                                main_list.append({
                                                    'Invoice_no':inv.name,
                                                    'date_order':hotel.hotel_return.date_order,
                                                    'arrival_date':hotel.hotel_return.arrival_date,
                                                    'customer_name':customer_name,
                                                    'room_type':room_type_list,
                                                    'get_Hotel_name':hotel.hotel_id.name,
                                                    'no_of_guest':hotel.no_of_person,
                                                    'rq_number':inv.package_no,
                                                    'Hotel_name':Hotel_name,
                                                    'check_in':date_from,
                                                    'check_out':date_to,
                                                    'nights':nights,
                                                    'amount_fc':amnt_fc,
                                                    'currency_id':currency,
                                                    'toatal_pkage_amount':inv.amount_total,
                                                    'creation_date':package.create_date,
                                                    'sale_person':package.user_id.name,
                                                    'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
                                                    })
                                                if same_suppliers ==1:
                                                    pkg_total += inv.amount_total

                    if booking_type !='book_date' and booking_type !='arrival_date' :
                        if report_type == 'hotel':
                            if inv.hotel_ids.ids in all_part_selected and hotel.hotel_id.id in all_part_selected_2:
                                for final in inv.hotel_ids:
                                    date_from = ""
                                    date_to = ""
                                    currency = ""
                                    nights = 0
                                    amnt_fc = 0
                                    currency_fc=0
                                    if final.id == hotel.hotel_id.id and final.id == x.id and hotel.hotel_id.id ==x.id:
                                        if hotel.supplier:
                                            if hotel.supplier.id == inv.partner_id.id:
                                                same_suppliers+=1
                                                customer_name = []
                                                room_type_list = []
                                                for t in hotel.room_type:
                                                    room_type_list.append(t.name)

                                                if hotel.customer_m2m:
                                                    for y in hotel.customer_m2m:
                                                        customer_name.append(y.name)

                                                amnt_fc += hotel.amnt_fc
                                                nights += hotel.nights*hotel.room_qty
                                                if not date_from:
                                                    date_from = hotel.date_from
                                                else:
                                                    date_from = str(date_from)+"/"+str(hotel.date_from)
                                                if not date_to:
                                                    date_to = hotel.date_to
                                                else:
                                                    date_to = str(date_to)+"/"+str(hotel.date_to)
                                                if not currency:
                                                    currency = hotel.currency_name.name
                                                else:
                                                    currency = str(currency)+"/"+str(hotel.currency_name.name)

                                                if inv.amount_total:
                                                    if report_type == 'hotel':
                                                        all_hotels = []
                                                        for ah in inv.hotel_ids:
                                                            if ah.id == x.id:
                                                                all_hotels.append(ah.name)

                                                        Hotel_name = all_hotels
                                                    if report_type == 'vendor':
                                                        Hotel_name = inv.partner_id.name
                                                    if report_type == 'destination':
                                                        Hotel_name = inv.partner_id.country_id.name

                                                    main_list.append({
                                                        'Invoice_no':inv.name,
                                                        'date_order':hotel.hotel_return.date_order,
                                                        'arrival_date':hotel.hotel_return.arrival_date,
                                                        'customer_name':customer_name,
                                                        'room_type':room_type_list,
                                                        'no_of_guest':hotel.no_of_person,
                                                        'rq_number':inv.package_no,
                                                        'Hotel_name':Hotel_name,
                                                        'check_in':date_from,
                                                        'check_out':date_to,
                                                        'nights':nights,
                                                        'amount_fc':amnt_fc,
                                                        'currency_id':currency,
                                                        'toatal_pkage_amount':inv.amount_total,
                                                        'creation_date':package.create_date,
                                                        'sale_person':package.user_id.name,
                                                        'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
                                                        })
                                                    if same_suppliers==1:
                                                        pkg_total += inv.amount_total
                        else:
                            date_from = ""
                            date_to = ""
                            currency = ""
                            nights = 0
                            amnt_fc = 0
                            currency_fc=0
                            if hotel.supplier:
                                if hotel.supplier.id == inv.partner_id.id:
                                    same_suppliers+=1
                                    customer_name = []
                                    room_type_list = []
                                    for t in hotel.room_type:
                                        room_type_list.append(t.name)

                                    if hotel.customer_m2m:
                                        for y in hotel.customer_m2m:
                                            customer_name.append(y.name)

                                    amnt_fc += hotel.amnt_fc
                                    nights += hotel.nights*hotel.room_qty
                                    if not date_from:
                                        date_from = hotel.date_from
                                    else:
                                        date_from = str(date_from)+"/"+str(hotel.date_from)
                                    if not date_to:
                                        date_to = hotel.date_to
                                    else:
                                        date_to = str(date_to)+"/"+str(hotel.date_to)
                                    if not currency:
                                        currency = hotel.currency_name.name
                                    else:
                                        currency = str(currency)+"/"+str(hotel.currency_name.name)

                                    if inv.amount_total:
                                        if report_type == 'hotel':
                                            all_hotels = []
                                            for ah in inv.hotel_ids:
                                                if ah.id == x.id:
                                                    all_hotels.append(ah.name)

                                            Hotel_name = all_hotels
                                        if report_type == 'vendor':
                                            Hotel_name = inv.partner_id.name
                                        if report_type == 'destination':
                                            Hotel_name = ''
                                            selected_dest_ids = country_id.ids  # wizard se selected destinations

                                            for rec in hotel.hotel_return:
                                                for des in rec.destination:
                                                    if des.id in selected_dest_ids:
                                                        Hotel_name = des.name
                                                        break

                                        main_list.append({
                                            'Invoice_no':inv.name,
                                            'date_order':hotel.hotel_return.date_order,
                                            'arrival_date':hotel.hotel_return.arrival_date,
                                            'customer_name':customer_name,
                                            'room_type':room_type_list,
                                            'get_Hotel_name':hotel.hotel_id.name,
                                            'no_of_guest':hotel.no_of_person,
                                            'rq_number':inv.package_no,
                                            'Hotel_name':Hotel_name,
                                            'check_in':date_from,
                                            'check_out':date_to,
                                            'nights':nights,
                                            'amount_fc':amnt_fc,
                                            'currency_id':currency,
                                            'toatal_pkage_amount':inv.amount_total,
                                            'creation_date':package.create_date,
                                            'sale_person':package.user_id.name,
                                            'status':dict(inv._fields['payment_state'].selection).get(inv.payment_state),
                                            })
                                        if same_suppliers==1:
                                            pkg_total += inv.amount_total


            if pkg_total > 0:
                hotel_summary_list.append({
                    'hotel_name':x.name,
                    'pkg_total':pkg_total,
                    })

            if main_list:
                hotel_main_list.append({
                    'hotel':x.name,
                    'serial_total':serial_total,
                    'main_list':main_list,
                    'pkg_total':pkg_total,
                    })



        # return {
        #     'doc_ids': docids,
        #     'doc_model':'account.move',
        #     'form': form,
        #     'to': to,
        #     'report_type': report_type,
        #     'company': company,
        #     'hotel_main_list': hotel_main_list,
        #     'hotel_summary_list': hotel_summary_list,
        # }



        if hotel_summary_list:

            worksheet_hotel_summery = workbook.add_worksheet('Summery Report')

            accounting_format = workbook.add_format({'num_format': '#,###0.00'})
            h4_bold = workbook.add_format({'bold': True, 'align': 'left', 'font_size': 10})

            worksheet_hotel_summery.write(1, 1, company.name, h4_bold)
            worksheet_hotel_summery.write(2, 1, company.street, h4_bold)
            worksheet_hotel_summery.write(3, 1, company.street2, h4_bold)
            worksheet_hotel_summery.write(4, 1, company.city, h4_bold)
            worksheet_hotel_summery.write(5, 1, company.country_id.name, h4_bold)

            worksheet_hotel_summery.write(6, 1, 'CR No:', h4_bold)
            worksheet_hotel_summery.write(6, 2, company.company_registry, h4_bold)

            worksheet_hotel_summery.write(7, 1, 'Ph:', h4_bold)
            worksheet_hotel_summery.write(7, 2, company.phone, h4_bold)

            worksheet_hotel_summery.write(8, 1, 'Company Email:', h4_bold)
            worksheet_hotel_summery.write(8, 2, company.email, h4_bold)

            worksheet_hotel_summery.write(9, 1, 'VAT', h4_bold)
            worksheet_hotel_summery.write(9, 2, company.vat, h4_bold)

            title_format = workbook.add_format({
                'align': 'center',
                'font_size': 15,
                'underline': True
            })

            date_format = workbook.add_format({
                'align': 'center',
                'font_size': 13,
                'underline': True
            })

            worksheet_hotel_summery.merge_range(11, 1, 11, 4, 'Hotel Production Report', title_format)

            date_text = 'From: ' + str(form) + ' TO: ' + str(to)
            worksheet_hotel_summery.merge_range(12, 1, 12, 4, date_text, date_format)

            header_format = workbook.add_format({
                'align': 'center',
                'font_size': 10,
                'underline': True,
                'bold': True,
                'fg_color': '#eaded7',
                'text_wrap': True
            })

            total_format = workbook.add_format({
                'align': 'center',
                'font_size': 10,
                'bold': True,
                'fg_color': '#eaded7',
                'text_wrap': True,
                'num_format': '#,##0.00'
            })

            worksheet_hotel_summery.set_row(14, 40)

            if report_type == 'hotel':
                worksheet_hotel_summery.merge_range(14, 1, 14, 3, 'Hotel Name', header_format)

            elif report_type == 'vendor':
                worksheet_hotel_summery.merge_range(14, 1, 14, 3, 'Vendor Name', header_format)

            elif report_type == 'destination':
                worksheet_hotel_summery.merge_range(14, 1, 14, 3, 'Destination Name', header_format)

            worksheet_hotel_summery.merge_range(14, 4, 14, 7, 'Total Bill Amount by SAR', header_format)

            worksheet_hotel_summery.set_column(1, 7, 20)

            row = 14
            total_pkg_total = 0

            for x in hotel_summary_list:

                row += 1

                worksheet_hotel_summery.merge_range(row, 1, row, 3, x['hotel_name'])

                worksheet_hotel_summery.merge_range(
                    row,
                    4,
                    row,
                    7,
                    x['pkg_total'],
                    accounting_format
                )

                total_pkg_total += x['pkg_total']

            # Total Row
            row += 1

            worksheet_hotel_summery.merge_range(
                row,
                1,
                row,
                3,
                'Total',
                total_format
            )

            worksheet_hotel_summery.merge_range(
                row,
                4,
                row,
                7,
                total_pkg_total,
                total_format
            )

        ##########################################################################
        ####################### Data for Hotel Detailed Starts ########################
        ######################################################################
        hotel_row = 2
        unique_hotel = []
        count = 1
        row = 3

        for x in hotel_main_list:
            Hotel_name = x['hotel']
            
            # Check if the hotel name is already in the unique_hotel list
            if Hotel_name not in unique_hotel:
                unique_hotel.append(Hotel_name)
                count = 1  # Reset count for new hotel
            else:
                count += 1  # Increment count for duplicate hotel names
                Hotel_name = f" {count}-{x['hotel']}"  # Create a unique name

            # print("_RRG__")
            # print(Hotel_name)
            # print("_RRG__")
            
            # Add the worksheet with the unique hotel name
            worksheet_hotel_report = workbook.add_worksheet(Hotel_name)
            accounting_format = workbook.add_format({'num_format': '#,##0.00'})
            cell_format = workbook.add_format({'align': 'left', 'font_size': 20, 'underline': True})
            headibng_format = workbook.add_format({'align': 'left', 'font_size': 15})
            worksheet_hotel_report.set_row(0, 40)
            worksheet_hotel_report.write(0, 5, 'Hotel Production Report', cell_format)
            date = 'From: '+str(form)+' TO: '+ str(to)
            worksheet_hotel_report.write(1, 5, date)
            worksheet_hotel_report.set_row(4, 40)
            worksheet_hotel_report.write(hotel_row,1, x['hotel'],headibng_format)
            # worksheet_hotel_report.write(hotel_row,2, x['destination'],headibng_format)
            worksheet_hotel_report.set_row(4, 40)
            detailed_formate = workbook.add_format({'align': 'centre', 'font_size': 12,'underline': True,'bold': True, 'fg_color': '#eaded7', 'text_wrap': True,'num_format': '#,##0.00'})

            total_formate = workbook.add_format({'align': 'centre', 'font_size': 12,'bold': True, 'fg_color': '#eaded7', 'text_wrap': True,'num_format': '#,##0.00'})
            worksheet_hotel_report.set_column(4, 40)
            worksheet_hotel_report.write(row, 0, 'Invoice No', detailed_formate)
            worksheet_hotel_report.write(row, 1, 'Branch', detailed_formate)
            worksheet_hotel_report.set_column(1, 1, 22)
            worksheet_hotel_report.write(row, 2, 'RQ No', detailed_formate)
            worksheet_hotel_report.set_column(2, 2, 22)
            worksheet_hotel_report.write(row, 3, 'Customer Name', detailed_formate)
            worksheet_hotel_report.set_column(3, 3, 22)
            worksheet_hotel_report.write(row, 4, 'Hotel Name', detailed_formate)

            worksheet_hotel_report.set_column(4, 4, 22)
            worksheet_hotel_report.write(row, 5, 'Room Type', detailed_formate)

            worksheet_hotel_report.set_column(5, 5, 22)
            worksheet_hotel_report.write(row, 6, 'No of Guest', detailed_formate)
            worksheet_hotel_report.set_column(6, 6, 22)


            worksheet_hotel_report.write(row, 7, 'Book Date', detailed_formate)
            worksheet_hotel_report.set_column(7, 7, 22)
            worksheet_hotel_report.write(row, 8, 'Arrival Date', detailed_formate)
            worksheet_hotel_report.set_column(8, 8, 22)


            worksheet_hotel_report.write(row, 9, 'Check In', detailed_formate)
            worksheet_hotel_report.set_column(9, 9, 22)
            worksheet_hotel_report.write(row, 10, 'Check Out', detailed_formate)
            worksheet_hotel_report.set_column(10, 10, 22)
            worksheet_hotel_report.write(row, 11, 'Total Nights', detailed_formate)
            worksheet_hotel_report.set_column(11, 11, 22)
            worksheet_hotel_report.write(row, 12, 'Amount FC', detailed_formate)
            worksheet_hotel_report.set_column(12, 12, 22)
            worksheet_hotel_report.write(row, 13, 'Currency', detailed_formate)
            worksheet_hotel_report.set_column(13, 13, 22)
            worksheet_hotel_report.write(row, 14, 'Total Bill Amount by SAR', detailed_formate)
            worksheet_hotel_report.set_column(14, 14, 22)
            worksheet_hotel_report.write(row, 15, 'Creation Date', detailed_formate)
            worksheet_hotel_report.set_column(15, 15, 22)
            # worksheet_hotel_report.set_column(13, 13, 22)
            worksheet_hotel_report.write(row, 16, 'Sales Person', detailed_formate)
            worksheet_hotel_report.set_column(17, 17, 22)
            worksheet_hotel_report.write(row, 17, 'Bill Status', detailed_formate)
            worksheet_hotel_report.freeze_panes(1, 0, 1, 0)
            # worksheet_hotel_report.freeze_panes(1, 0, 1, 0)
            line = row
            total_nights = 0
            total_guest = 0
            total_amount_fc = 0
            toatal_pkage_amount = 0
            for data in x['main_list']:
                rooms = ''
                for data_room_type in data['room_type']:
                    rooms += data_room_type

                customer_name_custom = ''
                for data_customers in data['customer_name']:
                    # customer_name_custom = data_customers +'\n'+ customer_name_custom
                    customer_name_custom += data_customers
                line += 1
                # print(row)                    
                # creation_date = datetime.datetime.strftime(data['creation_date'], "%Y-%m-%d")
                worksheet_hotel_report.write(line, 0, data['Invoice_no'])
                worksheet_hotel_report.write(line, 2, data['rq_number'])
                # if report_type == 'vendor':
                worksheet_hotel_report.write(line, 3, customer_name_custom)


                all_h_n = ""
                for h in data['Hotel_name']:
                    all_h_n +='%s \n'%h


                if report_type == 'hotel':
                    worksheet_hotel_report.write(line, 4, all_h_n)

                else:
                    worksheet_hotel_report.write(line, 4, data['get_Hotel_name'])

                
                worksheet_hotel_report.write(line, 5,rooms )
                # if report_type == 'destination':
                #     worksheet_hotel_report.write(line, 2, data['Destination'])
                worksheet_hotel_report.write(line, 6, str(data['no_of_guest']))
                worksheet_hotel_report.write(line, 7, str(data['date_order']+timedelta(hours=5)))
                worksheet_hotel_report.write(line, 8, str(data['arrival_date']))

                worksheet_hotel_report.write(line, 9, str(data['check_in']))
                worksheet_hotel_report.write(line, 10, str(data['check_out']))


                worksheet_hotel_report.write(line, 11, float(data['nights']),accounting_format)
                worksheet_hotel_report.write_number(line, 12, float(data['amount_fc']), accounting_format)
                # worksheet_hotel_report.write(line, 5, data['amount_fc'])
                worksheet_hotel_report.write(line, 13, data['currency_id'])
                # worksheet_hotel_report.write(line, 7, data['toatal_pkage_amount'])
                worksheet_hotel_report.write_number(line, 14, float(data['toatal_pkage_amount']), accounting_format)
                worksheet_hotel_report.write(line,15, str(data['creation_date']))
                worksheet_hotel_report.write(line, 16, data['sale_person'])
                worksheet_hotel_report.write(line, 17, data['status'])
                total_nights += data['nights']
                total_guest += data['no_of_guest']
                total_amount_fc += data['amount_fc']
                toatal_pkage_amount += data['toatal_pkage_amount']
            line += 1
            worksheet_hotel_report.write(line, 0, 'Total', total_formate)
            worksheet_hotel_report.write(line, 1, '-', total_formate)
            worksheet_hotel_report.write(line, 2, '-', total_formate)
            worksheet_hotel_report.write(line, 3, '-', total_formate)
            worksheet_hotel_report.write(line, 4, '-', total_formate)
            worksheet_hotel_report.write(line, 5, '-', total_formate)
            worksheet_hotel_report.write(line, 6, total_guest, total_formate,)
            worksheet_hotel_report.write(line, 7, '-', total_formate)
            worksheet_hotel_report.write(line, 8, '-', total_formate)
            worksheet_hotel_report.write(line, 9, '-', total_formate)
            worksheet_hotel_report.write(line, 10, '-', total_formate)
            worksheet_hotel_report.write(line, 11, total_nights, total_formate)
            worksheet_hotel_report.write(line, 12, total_amount_fc, total_formate)
            worksheet_hotel_report.write(line, 13, '-', total_formate)
            worksheet_hotel_report.write(line, 14, toatal_pkage_amount,total_formate)
            worksheet_hotel_report.write(line, 15, '-' , total_formate)
            worksheet_hotel_report.write(line, 16, '-', total_formate)
            worksheet_hotel_report.write(line, 17, '-', total_formate)