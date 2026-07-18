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

from odoo import models, fields, api,_
from datetime import date
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta
import dateutil.parser
import math
from odoo.exceptions import ValidationError, UserError
import json
import odoo.exceptions
import datetime as dt
import requests
from odoo import http
from odoo.http import request
import http.client
from lxml import etree
import logging
import base64
from collections import defaultdict
from contextlib import ExitStack, contextmanager
from odoo.tools.misc import format_amount



_logger = logging.getLogger(__name__)



class HotelArrival(models.Model):
    _name = 'hotel.arrival'
    _description = 'Hotel Arrival'
    name = fields.Char("Name")

class TermsCondtionsForm(models.Model):
    _name = 'terms.condtions'
    _description = "Term and Conditions"

    def _get_default_note(self):

        result = """
            <div dir="rtl" style="text-align:right;margin-right:30px;">
                <ol>
                    <li>‫للطائرة‬ ‫الصعود‬ ‫من‬ ‫ساعة‬ ‫‪72‬‬ ‫)قبل‬ ‫‪19‬‬ ‫‪-‬‬ ‫كوفيد‬ ‫(‬ ‫ل‬ ‫سلبية‬ ‫بنتيجة‬ ‫فحص‬ ‫للمالديف‬ ‫المسافرين‬ ‫جميع‬ ‫يلزم‬ ‫‪2020‬‬ ‫ب‬ ‫سبتم‬ ‫‪10‬‬ ‫من‬ ‫بتداءا‬ ‫إ‬ الرسائل‬ ‫تقبل‬ ‫وال‬ ‫ية‬ ‫االنجلب‬ ‫وباللغة‬ ‫مطبوعة‬ ‫الفحص‬ ‫نتيجة‬ ‫تكون‬ ‫ان‬ ‫يجب‬ ‫‪,‬‬ ‫شهرا‬ ‫‪12‬‬ ‫ال‬ ‫سن‬ ‫دون‬ ‫الرضع‬ ‫ذلك‬ ‫من‬ ‫ويعف‬ ‫اقىص‬ ‫بحد‬ ‫الجوال‪.‬‬ ‫عىل‬ ‫االشعارات‬ ‫أو‬ ‫‪.‬النصية‬</li>

                    <li>‫ف‬ ‫التأخب‬ ‫لتجنب‬ ‫ساعة‬ ‫‪24‬‬ ‫ب‬ ‫منها‬ ‫والمغادرة‬ ‫للمالديف‬ ‫الوصول‬ ‫قبل‬ ‫مسافر‬ ‫لكل‬ ‫هنا‬ ‫إضغط‬ ‫الصح‬ ‫اإلفصاح‬ ‫نموذج‬ ‫تعبئة‬ ‫يجب‬ السفر‪.‬‬ ‫اجراءات‬ </li>

                    <li>‫المنتجع‪.‬‬ ‫باسم‬ ‫او‬ ‫العميل‬ ‫باسم‬ ‫بلوحة‬ ‫بالمنتجع‬ ‫الخاص‬ ‫المندوب‬ ‫طريق‬ ‫عن‬ ‫يكون‬ ‫المطار‬ ‫ف‬ ‫االستقبال‬</li>

                    <li>‫الحجز‪.‬‬ ‫حسب‬ ‫بكم‬ ‫الخاصة‬ ‫النقل‬ ‫وسيلة‬ ‫اىل‬ ‫بأخذكم‬ ‫المندوب‬ ‫يقوم‬ ‫س‬</li>

                    <li>‫يد‪.‬‬ ‫شنطة‬ ‫كيلو‬ ‫‪3‬‬ ‫‪+‬‬ ‫شخص‬ ‫لكل‬ ‫كيلو‬ ‫‪20‬‬ ‫هو‬ ‫المائية‬ ‫الطائرة‬ ‫ف‬ ‫المسموح‬ ‫الوزن‬</li>



                    <li>‫يد‪.‬‬ ‫شنطة‬ ‫كيلو‬ ‫‪5‬‬ ‫‪+‬‬ ‫شخص‬ ‫لكل‬ ‫كيلو‬ ‫‪20‬‬ ‫هو‬ ‫الداخلية‬ ‫الرحلة‬ ‫ف‬ ‫المسموح‬ ‫الوزن‬</li>

                    <li>‫يد‪.‬‬ ‫شنطة‬ ‫كيلو‬ ‫‪5‬‬ ‫‪+‬‬ ‫شخص‬ ‫ل‬ ‫لك‬ ‫كيلو‬ ‫‪25‬‬ ‫هو‬ ‫ع‬ ‫الرسي‬ ‫القارب‬ ‫ف‬ ‫المسموح‬ ‫الوزن‬</li>

                    <li>‫‪‫‪.‬‬ ‫األمريك‬ ‫الدوالر‬ ‫ه‬ ‫المالديف‬ ‫مطار‬ ‫ف‬ ‫المستخدمة‬ ‫العملة‬</li>

                    <li>‫الوصول‪.‬‬ ‫عند‬ ‫المنتجع‬ ‫طريق‬ ‫عن‬ ‫وتكون‬ ‫السعر‬ ‫ف‬ ‫مشمولة‬ ‫غب‬ ‫البحرية‬ ‫األنشطة‬ ‫جميع‬</li>

                    <li>‫عرصا‪.‬‬ ‫‪3:30‬‬ ‫اىل‬ ‫صباحا‬ ‫‪8:30‬‬ ‫بي‬ ‫ما‬ ‫المائية‬ ‫الطائرة‬ ‫أوقات‬</li>

                    <li>‫االستقبال‪.‬‬ ‫عند‬ ‫المندوب‬ ‫من‬ ‫مساعدة‬ ‫بطلب‬ ‫المطار‬ ‫من‬ ‫يحة‬ ‫ش‬ ‫ر‬ ‫اء‬ ‫ش‬ ‫ر‬ ‫ويمكن‬ ‫مجانا‬ ‫فاي‬ ‫الواي‬ ‫توفر‬ ‫المنتجعات‬ ‫جميع‬</li>

                    <li>‫جعات‪.‬‬ ‫المنت‬ ‫ف‬ ‫كامل‬ ‫بشكل‬ ‫تعمل‬ ‫وجميعها‬ ‫)‬ ‫إئتمانية‬ ‫بطاقة‬ ‫–‬ ‫نقدا‬ ‫(‬ ‫ماليا‬ ‫المالديف‬ ‫ف‬ ‫التعامل‬ ‫يمكن‬</li>

                    <li>‫درجة‪.‬‬ ‫‪30‬‬ ‫‪-‬‬ ‫‪28‬‬ ‫بي‬ ‫معتدلة‬ ‫العام‬ ‫طوال‬ ‫المالديف‬ ‫ف‬ ‫الحرارة‬ ‫درجة‬</li>

                    <li>‫الجنسيات‪.‬‬ ‫لجميع‬ ‫مسبقة‬ ‫دخول‬ ‫ة‬ ‫تأشب‬ ‫اىل‬ ‫المالديف‬ ‫تحتاج‬ ‫ال‬</li>
                <ol/>
            </div>"""

        return result

    name = fields.Char("Name")
    flights_cancel_policy = fields.Text("Flight Terms & Conditions and Remarks")
    hotels_cancel_policy = fields.Text("Hotel Terms & Conditions and Remarks")
    transfers_cancel_policy = fields.Text("Transfer Terms & Conditions and Remarks")
    tours_cancel_policy = fields.Text("Tour Terms & Conditions and Remarks")
    visa_cancel_policy = fields.Text("Visa Terms & Conditions and Remarks")
    packages_cancel_policy = fields.Text("Ready Package Terms & Conditions and Remarks")
    private_jet_cancel_policy = fields.Text("Private Terms & Conditions and Remarks")
    yacht_cancel_policy = fields.Text("Yacht Terms & Conditions and Remarks")
    cruise_cancel_policy = fields.Text("Cruise Terms & Conditions and Remarks")
    other_cancel_policy = fields.Text("Other Terms & Conditions and Remarks")
    voucher_cancel_policy = fields.Text("Terms & Conditions and Remarks")

class HotelRturn(models.Model):
    _name = 'hotel.return'
    _description = "Hotel Return"
    
    name = fields.Char("Name")

class sale_order_customized(models.Model):
    _name = 'reservation.order'
    _description = 'Reservation'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    payment_term = fields.Char("Payment Term")
    payment_date_custom = fields.Date("Due Payment Date")
    x_flight_detail = fields.Boolean(string="Flight Details")
    image = fields.Binary(tracking=True)
    name_package=fields.Char("Package Name", tracking=True)
    year=fields.Char("Year", tracking=True)
    package = fields.Boolean("Is Package")
    stamp = fields.Boolean("Stamp")
    active = fields.Boolean("Active",default=1)
    quote_builder = fields.Boolean("Is Quote")
    stages = fields.Selection([
        ('draft', 'Draft'),
        ('validate', 'Confirm'),
        ('cancel', 'Canceled'),
    ],default='draft', tracking=True,copy=False)
    reservation_type = fields.Selection([
        ('b2b', 'B2B'),
        ('b2c', 'B2C'),
    ], tracking=True)
    name = fields.Char(string="Name", default="New", copy=False)
    date_order = fields.Datetime(
        string="Order Date",
        required=True, copy=False,
        help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.",
        default=fields.Datetime.now)
    partner_id = fields.Many2one('res.partner',string="Customer")
    job_of_company= fields.Many2one('company.name',string="Company Name", tracking=True)
    hotel_arrival= fields.Many2one('hotel.arrival',string="Arrival Flight", tracking=True)
    hotel_return= fields.Many2one('hotel.return',string="Departure Flight", tracking=True)
    package_reference= fields.Many2one('reservation.order',string="Package Reference", tracking=True)

    no_of_particpents=fields.Integer("No of Guests", tracking=True)
    destination = fields.Many2many('destination.name', string ="Destination", tracking=True)
    arrival_date= fields.Date('Arrival Date', tracking=True)
    departure_date= fields.Date('Departure Date', tracking=True)
    agent =fields.Many2one('res.partner', string ="Sub-Agent" ,domain="[('travel_agency','=',True)]", tracking=True)
    invoice_add =fields.Char("Invoice Address", tracking=True)
    delivery_add =fields.Char("Delievery Address", tracking=True)
    quotation_template =fields.Many2one('quot.name', string ="Quotation Template", tracking=True)
    get_term_conditions =fields.Many2one('terms.condtions', string ="General Instructions")
    partner_id_mtom = fields.Many2many('res.partner', string ="Family List", compute="_get_guest_info_m2m",store=False)
    price_list =fields.Many2one('product.pricelist', string ="Product Pricelist ", tracking=True)
    customer_ref= fields.Char(string="Customer Reference", tracking=True)
    validity_date= fields.Date("Validity Date", tracking=True)
    itinarnay_package= fields.One2many('all.services','itinarnay_return' , tracking=True)
    cost_manage = fields.One2many('cost.manage','manage_return', tracking=True)
    transportation_pkg = fields.One2many('all.services','transportation_return', tracking=True,copy=True)
    tours_pkg = fields.One2many('all.services','tours_return', tracking=True,copy=True)
    visa_pkg = fields.One2many('all.services','visa_return', tracking=True,copy=True)
    hotel_pkg = fields.One2many('all.services','hotel_return', tracking=True,copy=True)
    flights_pkg = fields.One2many('all.services','flights_return', tracking=True,copy=True)
    services_pkg = fields.One2many('all.services','services_return', tracking=True,copy=True)
    packages_pkg = fields.One2many('all.services','package_return', tracking=True,copy=True)
    privatejet_pkg = fields.One2many('all.services','privatejet_return', tracking=True,copy=True)
    yacht_pkg = fields.One2many('all.services','yacht_return', tracking=True,copy=True)
    cruises_pkg = fields.One2many('all.services','cruises_return', tracking=True,copy=True)
    otherservices_pkg = fields.One2many('all.services','otherservices_return', tracking=True,copy=True)
    journal_entry =fields.Many2one('account.move', string ="Journal Entry", tracking=True)
    sales_team =fields.Many2one('crm.team', string ="Sales Team", tracking=True)
    show_details=fields.Boolean(string ="Show more details")
    include_visa_price=fields.Boolean(string ="Include Visa Price")
    include_ticket_price=fields.Boolean(string ="Include Ticket Price")
    per_person_single = fields.Float("Per Person in Single", tracking=True)
    per_person_double = fields.Float("Per Person in Double", tracking=True)
    per_person_triple= fields.Float("Per Person in Triple", tracking=True)
    cwnb = fields.Float("CWNB", tracking=True)
    usd_currency = fields.Many2one('usd.currency',"USD Currency", tracking=True)
    per_person_dbl = fields.Float("Per Person in DBL", tracking=True)
    per_person_sgl = fields.Float("Per Person in SGL", tracking=True)
    per_person_tpl = fields.Float("Per Person in TPL", tracking=True)
    usd_cwnb = fields.Float("USD CWNB", tracking=True)
    profit_price = fields.Float("Profit Price", tracking=True)

    rec_count = fields.Integer('Count', compute='_compute_count_func', tracking=True)
    rec_count_inv = fields.Integer('Count Invoice', compute='_compute_count_func_inv', tracking=True)
    cust_credits_count = fields.Integer('Count Customer Credits', compute='_compute_count_func_inv', tracking=True)
    vendor_credits_count = fields.Integer('Count Vendor Credits', compute='_compute_count_func', tracking=True)
    travel_consultant =fields.Boolean(string="Travel Consultant Confirmation")
    email_count = fields.Integer(string="Email Count")
    flights_commission = fields.Float("Flight Commission", tracking=True)
    hotels_commission = fields.Float("Hotel Commission", tracking=True)
    transfer_commission = fields.Float("Transfer Commission", tracking=True)
    tours_commission = fields.Float("Tours Commission", tracking=True)
    visa_commission = fields.Float("Visa Commission", tracking=True)
    packages_commission = fields.Float("Package Commission", tracking=True)
    private_jet_commission = fields.Float("Private Jet Commission", tracking=True)
    yacht_commission = fields.Float("Yacht Commission", tracking=True)
    cruises_commission = fields.Float("Cruise Commission", tracking=True)
    other_services_commission = fields.Float("Other Service Commission", tracking=True)
    total_commission = fields.Float("Total Commission", tracking=True)
    package_total = fields.Float("Package Total", compute="get_package_total", store=True, tracking=True)
    reason_to_cancel = fields.Html("Reason to Cancel")
    summary = fields.Boolean("Summary",tracking=True)

    flights_cancel_policy = fields.Html("Terms & Conditions and Remarks")
    hotels_cancel_policy = fields.Html("Terms & Conditions and Remarks")
    transfers_cancel_policy = fields.Html("Terms & Conditions and Remarks")
    tours_cancel_policy = fields.Html("Terms & Conditions and Remarks")
    visa_cancel_policy = fields.Html("Terms & Conditions and Remarks")
    packages_cancel_policy = fields.Html("Terms & Conditions and Remarks")
    private_jet_cancel_policy = fields.Html("Terms & Conditions and Remarks")
    yacht_cancel_policy = fields.Html("Terms & Conditions and Remarks")
    cruise_cancel_policy = fields.Html("Terms & Conditions and Remarks")
    other_cancel_policy = fields.Html("Terms & Conditions and Remarks")
    # credit_limit_check = fields.Boolean(string="Credit Limit Check")
    credit_limit_reached = fields.Html(string="Credit Limit Reached")
    commissioned = fields.Boolean(string="Employee Commission")

    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)
    serial_no = fields.Char(string='Serial No', default='/', copy=False, tracking=True)
    user_id = fields.Many2one(
        comodel_name='res.users',
        string="Salesperson",
        default=lambda self: self.env.user,
        store=True, readonly=False, precompute=True, index=True,
        tracking=2,)

    custom_invoice_status = fields.Selection([
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
        ], string='Invoice Status', readonly=True)
    custom_invoice_status_compute = fields.Boolean(compute='_get_cust_invoice_status')
    custom_image = fields.Binary(string="Email Image")
    invoice_exist = fields.Boolean('Invoice Exist')
    bill_exist = fields.Boolean('Bill Exist')
    field_to_run_function = fields.Boolean(compute='_check_invoices')

    c_k_amount_total =  fields.Float(string='Amount Total', required=False, readonly=True , default=0 , compute="_get_all_total_amount_c" , store=True)
    duplicate_sale_order_count = fields.Integer(
        string='Duplicate Sale Orders',
        compute='_compute_duplicate_sale_orders',
    )
    has_duplicate_sale_orders = fields.Boolean(
        string='Has Duplicate Sale Orders',
        compute='_compute_duplicate_sale_orders',
    )
    duplicate_sale_order_message = fields.Char(
        string='Duplicate Sale Order Message',
        compute='_compute_duplicate_sale_orders',
    )

    custom_invoice_status_new = fields.Selection([
        ('only_invoice', 'Only Invoice'),
        ('only_bill', 'Only Bill'),
        ('both_invoice_bill', 'Fully invoiced & Billed'),
        ('no_all', 'Nothing Posted')
        ], string='Invoice Status Custom', readonly=True)

    custom_invoice_status_new_compute = fields.Boolean()


    def get_cust_invoice_status_new(self):
        for rec in self:
            if rec.stages == 'validate':
                # Posted customer invoices
                invoice_posted = self.env['account.move'].search_count([
                    ('state', '=', 'posted'),
                    ('invoice_origin', 'like', rec.name),
                    ('move_type', '=', 'out_invoice')
                ])

                # All vendor bills (excluding cancel)
                all_bills = self.env['account.move'].search([
                    ('state', '!=', 'cancel'),
                    ('invoice_origin', 'like', rec.name),
                    ('move_type', '=', 'in_invoice')
                ])

                posted_bills = all_bills.filtered(lambda b: b.state == 'posted')

                if invoice_posted and all_bills and len(all_bills) == len(posted_bills):
                    rec.custom_invoice_status_new = 'both_invoice_bill'

                elif invoice_posted and not all_bills:
                    rec.custom_invoice_status_new = 'only_invoice'

                elif not invoice_posted and posted_bills:
                    rec.custom_invoice_status_new = 'only_bill'

                elif invoice_posted and all_bills and len(posted_bills) < len(all_bills):
                    rec.custom_invoice_status_new = 'only_invoice'  # some bills draft

                else:
                    rec.custom_invoice_status_new = 'no_all'
            else:
                rec.custom_invoice_status_new = 'no_all'


    @api.depends('itinarnay_package')
    def _get_all_total_amount_c(self):


        for data in self:

            if data.itinarnay_package:
                total = 0
                for x in data.itinarnay_package:
                    total+=x.total
                data.c_k_amount_total = total

            else:
                data.c_k_amount_total = 0

    @api.depends('partner_id', 'arrival_date')
    def _compute_duplicate_sale_orders(self):
        for order in self:
            order.duplicate_sale_order_count = 0
            order.has_duplicate_sale_orders = False
            order.duplicate_sale_order_message = False

            if not order.partner_id or not order.arrival_date:
                continue

            duplicate_count = self.search_count([
                ('id', '!=', order.id or 0),
                ('partner_id', '=', order.partner_id.id),
                ('arrival_date', '=', order.arrival_date),
                ('stages', '=', 'validate'),
            ])
            order.duplicate_sale_order_count = duplicate_count
            order.has_duplicate_sale_orders = bool(duplicate_count)
            if duplicate_count:
                order.duplicate_sale_order_message = _(
                    "This Customer already has %s other reservation(s) with the same Arrival date."
                ) % duplicate_count

    def action_log_duplicate_sale_orders(self):
        self.ensure_one()
        salesperson_name = self.env.user.name or self.user_id.name or '-'
        body = _(
            "Duplicate reservation warning acknowledged by salesperson: %s"
        ) % salesperson_name
        self.message_post(body=body, subject=_("Duplicate Reservation Warning"))
        return True


    def send_email_fahad(self, reservation_order_ids):
        hr_employee_email = self.env['hr.employee'].search([('id','=',8)])
        sale_orders = self.env['reservation.order'].sudo().browse(reservation_order_ids)
        print("ii")
        print(sale_orders)
        print("ii")
        for rec in hr_employee_email:
            if rec.work_email:
                mail_obj = self.env['mail.mail']
                send_to = rec.work_email
                current_date = fields.Date.today()
                formatted_date = current_date.strftime("%d-%b-%Y")

                fahad_name = []
                if rec.name:
                    name_fahad = rec.name
                    fahad_name.append(name_fahad)

                form_design = """
                    <div style="width:100%; text-align:center;">
                    </div> 
                    <b>Hello</b>
                    <div style="width:100%";>
                        {%for person in fahad_name%}
                            <span style="font-weight:bold">{{person}}</span>
                        {%endfor%},
                        <br/>
                        <div>
                        <h4 style="margin-top:10px;">
                        <b style="color: black;">Please Download the attach pdf files and see the details </b> 
                    </h4>
                    </div>
                        <br/>
                        <br/>
                        <b>Regards:</b>
                        <br/>
                        Togather Travel
                        <br/>
                        <br/>
                        <div class="custom_footer" style="width:100%;">
                        </div>
                    </div>
                """

                email_from = self.env['ir.mail_server'].search([],limit=1)
                template = Environment(loader=BaseLoader).from_string(form_design)
                template_vars = {'fahad_name':fahad_name}
                html_out = template.render(template_vars)
                new_to_send_at_data_ids = []

                # for sale_order in sale_orders:
                new_report_template_id = self.env['ir.actions.report'].sudo()._render_qweb_pdf('email_voucher_report.email_voucher_report_pdf_email',sale_orders.ids)
                new_data_record = base64.b64encode(new_report_template_id[0])
                ir_values = {
                    'name': "Daily Arrival Report- Reservation.pdf",
                    # .format("sale_orders")
                    'type': 'binary',
                    'datas': new_data_record,
                    'store_fname': new_data_record,
                    'mimetype': 'application/pdf',
                }

                n_data_id = self.env['ir.attachment'].sudo().create(ir_values)
                new_to_send_at_data_ids.append(n_data_id.id)

                my_mail = mail_obj.create({
                    'attachment_ids': [(6, 0, new_to_send_at_data_ids)],
                    'email_from': email_from.smtp_user,
                    'email_to': send_to,
                    'model': 'hr.employee',
                    'res_id': rec.id,
                    'subject': "Daily Arrival Report-" + str(formatted_date),
                    'body_html': '''<span style="font-size: 14px"><br/><br/>%s</span>''' % (html_out)
                }).send()

    def send_email_to_fahad(self):
        days_plus = timedelta(days=1)
        current_date = fields.Date.today()
        sale_order = self.env['reservation.order'].sudo().search([('stages', '=', 'validate')])
        sale_order_ids_to_email = []
        for x in sale_order:
            one_day_after = current_date + days_plus
            if current_date < one_day_after:
                if x.arrival_date == one_day_after:
                    sale_order_ids_to_email.append(x.id)

        if sale_order_ids_to_email:
            self.send_email_fahad(sale_order_ids_to_email)#cron job

    def send_email_attia_arrival(self, reservation_order_ids):
        hr_employee_email = self.env['hr.employee'].search([('id','=',14)])
        sale_orders = self.env['reservation.order'].sudo().browse(reservation_order_ids)
        print("ii")
        print(sale_orders)
        print("ii")
        for employee in hr_employee_email:
            if employee.work_email:
                mail_obj = self.env['mail.mail']
                send_to = employee.work_email
                current_date = fields.Date.today()
                formatted_date = current_date.strftime("%d-%b-%Y")

                user_name = []
                if employee.name:
                    name_user = employee.name
                    user_name.append(name_user)

                form_design = """
                    <div style="width:100%; text-align:center;">
                    <img src="https://bucket.s3.ap-southeast-1.amazonaws.com/odoo/new_Logo.png"/>
                    </div> 
                    <b>Hello</b>
                    <div style="width:100%";>
                        {%for person in user_name%}
                            <span style="font-weight:bold">{{person}}</span>
                        {%endfor%},
                        <br/>
                        <div>
                        <h4 style="margin-top:10px;">
                        <b style="color: black;">Please Download the attach pdf files and see the details </b> 
                    </h4>
                    </div>
                        <br/>
                        <br/>
                        <b>Regards:</b>
                        <br/>
                        Togather Travel
                        <br/>
                        <br/>
                        <div class="custom_footer" style="width:100%;">
                        </div>
                    </div>
                """

                email_from = self.env['ir.mail_server'].search([],limit=1)
                template = Environment(loader=BaseLoader).from_string(form_design)
                template_vars = {'user_name':user_name}
                html_out = template.render(template_vars)
                new_to_send_at_data_ids = []

                # for sale_order in sale_orders:
                new_report_template_id = self.env['ir.actions.report'].sudo()._render_qweb_pdf('email_voucher_report.email_voucher_report_pdf_email',sale_orders.ids)
                new_data_record = base64.b64encode(new_report_template_id[0])
                ir_values = {
                    'name': "Daily Arrival Report- Reservation.pdf",
                    # .format("sale_orders")
                    'type': 'binary',
                    'datas': new_data_record,
                    'store_fname': new_data_record,
                    'mimetype': 'application/pdf',
                }

                n_data_id = self.env['ir.attachment'].sudo().create(ir_values)
                new_to_send_at_data_ids.append(n_data_id.id)

                my_mail = mail_obj.create({
                    'attachment_ids': [(6, 0, new_to_send_at_data_ids)],
                    'email_from': email_from.smtp_user,
                    'email_to': send_to,
                    'model': 'hr.employee',
                    'res_id': employee.id,
                    'subject': "Daily Arrival Report-" + str(formatted_date),
                    'body_html': '''<span style="font-size: 14px"><br/><br/>%s</span>''' % (html_out)
                }).send()

    def send_email_to_attia_arrival(self):
        days_plus = timedelta(days=1)
        current_date = fields.Date.today()
        sale_order = self.env['reservation.order'].sudo().search([('stages', '=', 'validate')])
        sale_order_ids_to_email = []
        for x in sale_order:
            one_day_after = current_date + days_plus
            if current_date < one_day_after:
                if x.arrival_date == one_day_after:
                    sale_order_ids_to_email.append(x.id)

        if sale_order_ids_to_email:
            self.send_email_attia_arrival(sale_order_ids_to_email)#cron job 

    def send_email_to_fahad_and_all_team(self, reservation_order_ids):
        sale_orders = self.env['reservation.order'].sudo().browse(reservation_order_ids)
        sales_groups = {}
        
        for sale_order in sale_orders:
            if sale_order.user_id:
                user_id = sale_order.user_id.id
                if not user_id:
                    continue
                if user_id and user_id not in [12, 14]:
                    if user_id not in sales_groups:
                        sales_groups[user_id] = []
                    sales_groups[user_id].append(sale_order.id)
            
        for users_arraivals in sales_groups:
            hr_employee_email = self.env['res.users'].search([('id', '=', users_arraivals)])
            sale_orders = self.env['reservation.order'].sudo().browse(sales_groups[users_arraivals])

            for rec in hr_employee_email:
                if rec.work_email:
                    mail_obj = self.env['mail.mail']
                    send_to = rec.work_email
                    current_date = fields.Date.today()
                    formatted_date = current_date.strftime("%d-%b-%Y")

                    fahad_name = []
                    if rec.name:
                        name_fahad = rec.name
                        fahad_name.append(name_fahad)

                    form_design = """ 
                        <div style="width:100%; text-align:center;">
                        </div> 
                        <b>Hello</b>
                        <div style="width:100%";>
                            {%for person in fahad_name%}
                                <span style="font-weight:bold">{{person}}</span>
                            {%endfor%},
                            <br/>
                            <div>
                            <h4 style="margin-top:10px;">
                            <b style="color: black;">Please Download the attached PDF files and see the details </b> 
                        </h4>
                        </div>
                            <br/>
                            <br/>
                            <b>Regards:</b>
                            <br/>
                            ogather Tourism
                            <br/>
                            <br/>
                            <div class="custom_footer" style="width:100%;">
                            </div>
                        </div>
                    """

                    email_from = self.env['ir.mail_server'].search([], limit=1)
                    template = Environment(loader=BaseLoader).from_string(form_design)
                    template_vars = {'fahad_name': fahad_name}
                    html_out = template.render(template_vars)
                    new_to_send_at_data_ids = []

                    # Generate PDF attachment
                    new_report_template_id = self.env['ir.actions.report'].sudo()._render_qweb_pdf('email_voucher_report.email_voucher_report_pdf_email',sale_orders.ids)
                    new_data_record = base64.b64encode(new_report_template_id[0])
                    ir_values = {
                        'name': "Daily Arrival Report- Reservation.pdf",
                        'type': 'binary',
                        'datas': new_data_record,
                        'store_fname': "Daily Arrival Report- Reservation.pdf",
                        'mimetype': 'application/pdf',
                    }

                    n_data_id = self.env['ir.attachment'].sudo().create(ir_values)
                    new_to_send_at_data_ids.append(n_data_id.id)

                    my_mail = mail_obj.create({
                        'attachment_ids': [(6, 0, new_to_send_at_data_ids)],
                        'email_from': email_from.smtp_user,
                        'email_to': send_to,
                        'model': 'res.users',
                        'res_id': rec.id,
                        'subject': "Daily Arrival Report-" + str(formatted_date),
                        'body_html': '''<span style="font-size: 14px"><br/><br/>%s</span>''' % (html_out)
                    }).send()

    def send_email_to_fahad_and_team(self):
        days_plus = timedelta(days=1)
        current_date = fields.Date.today()
        sale_order = self.env['reservation.order'].sudo().search([('stages', '=', 'validate')])
        sale_order_ids_to_email = []
        for x in sale_order:
            one_day_after = current_date + days_plus
            if current_date < one_day_after:
                if x.arrival_date == one_day_after:
                    sale_order_ids_to_email.append(x.id)
        if sale_order_ids_to_email:
            self.send_email_to_fahad_and_all_team(sale_order_ids_to_email)#cron job

    def _check_room_quantity(self):
        missing_tabs = []

        # Check Room Quantity for Hotel Package
        for record in self.hotel_pkg:
            if record.room_qty <= 0:
                raise ValidationError("Room quantity must be greater than zero in 'Hotel Tab'.")

        # Define Tabs for Currency Validation
        tab_mapping = {
            'hotel_pkg': "Hotel Tab",
            'flights_pkg': "Flights Tab",
            'transportation_pkg': "Transfer Tab",
            'tours_pkg': "Tours Tab",
            'visa_pkg': "Visa Tab",
            'packages_pkg': "Ready Packages Tab",
            'privatejet_pkg': "Private Jet Tab",
            'yacht_pkg': "Yacht Tab",
            'cruises_pkg': "Cruises Tab",
            'otherservices_pkg': "Other Services Tab",
        }

        # Check Missing Currencies
        for field_name, tab_name in tab_mapping.items():
            for record in getattr(self, field_name):
                if not record.currency_name:
                    if tab_name not in missing_tabs:
                        missing_tabs.append(tab_name)

        # Raise Single Validation Error if Any Tab is Missing Currency
        if missing_tabs:
            missing_tabs_str = ", ".join(missing_tabs)
            raise ValidationError(f"Currency is required in the following tabs: {missing_tabs_str}. Please select a currency.")

    def wizards_sms(self):
        return {
            'res_model': 'custom.sms',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'name':'Send SMS',
            'view_type': 'form',
            'target': 'new',
             'context': dict(
                default_send_to=self.partner_id.mobile,
            ),
            }

    def set_package_line_link(self):
        for package in self.search([]):
            for line in package.itinarnay_package:
                invoices = self.env['account.move'].search([('package_no','=',package.name)])
                for inv in invoices:
                    if inv.move_type in ['out_invoice','out_refund']:
                        price = line.total
                    if inv.move_type in ['in_invoice','in_refund']:
                        price = line.price
                    line_recs = self.env['account.move.line'].search([
                        ('move_id', '=', inv.id),
                        ('name','=',line.description+", "+package.name),
                        ('quantity','=',1),
                        ('price_unit','=',price),
                        ('currency_fc','=',line.currency_name.id),
                        ('product_id','=',line.product_id.id),
                        ])
                    for x in line_recs:
                        x.update({
                            'package_line':line.id,
                            })


    
    @api.depends('stages','rec_count_inv')
    def _get_cust_invoice_status(self):
        for rec in self:
            rec.custom_invoice_status_compute = True
            if rec.stages == 'validate':
                invoice = self.env['account.move'].search_count([('state','=','posted'),('invoice_origin', 'like', rec.name),('move_type','=','out_invoice')])
                if invoice:
                    rec.custom_invoice_status = 'invoiced'
                else:
                    rec.custom_invoice_status = 'to invoice'

            else:
                rec.custom_invoice_status = 'no'


    
    @api.depends('stages','rec_count','rec_count_inv')
    def _check_invoices(self):

        for rec in self:
            rec.field_to_run_function = True
            invoice = self.env['account.move'].search_count([('state','!=','cancel'),('invoice_origin', 'like', rec.name),('move_type','=','out_invoice')])
            bill = self.env['account.move'].search_count([('state','!=','cancel'),('invoice_origin', 'like', rec.name),('move_type','=','in_invoice')])

            if invoice:
                rec.invoice_exist = True
            else:
                rec.invoice_exist = False
            if bill:
                rec.bill_exist = True
            else:
                rec.bill_exist = False


    def create_pkg_from_quote(self):

        self.quote_builder = False


    def unlink(self):

        for record in self:
            if record.stages != 'draft':
                raise ValidationError('You cannot delete the record.')

            recs = self.env['all.services'].search([('services_return','=',False),('flights_return','=',False),('package_return','=',False),('yacht_return','=',False),('cruises_return','=',False),('privatejet_return','=',False),('otherservices_return','=',False),('tours_return','=',False),('itinarnay_return','=',False),('transportation_return','=',False),('hotel_return','=',False),('visa_return','=',False),])
            for x in recs:
                x.unlink()
        return super(sale_order_customized, self).unlink()


    def archive(self):
        self.active = False
    
    def unarchive(self):
        self.active = True

    def data_auto_correct(self):


        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }



    def action_voucher_sent(self):

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.check_object_reference('add_voucher_report', 'add_voucher_email_template')[1]
        except ValueError:
            template_id = False

        try:
            compose_form_id = ir_model_data.check_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
           'default_model': 'reservation.order',
           'default_res_ids': self.ids,
           'default_use_template': bool(template_id),
           'default_template_id': template_id,
           'default_composition_mode': 'comment',
        }
        return {
           'name': _('Voucher Email'),
           'type': 'ir.actions.act_window',
           'view_mode': 'form',
           'res_model': 'mail.compose.message',
           'views': [(compose_form_id, 'form')],
           'view_id': compose_form_id,
           'target': 'new',
           'context': ctx,
        }

    @api.depends('itinarnay_package.total')
    def get_package_total(self):
        for rec in self:
            rec.package_total = sum(rec.itinarnay_package.mapped('total'))

    def _get_default_note(self):

        result = """
            <div dir="rtl" style="text-align:right;margin-right:30px;">
                <ol>
                    <li>‫للطائرة‬ ‫الصعود‬ ‫من‬ ‫ساعة‬ ‫‪72‬‬ ‫)قبل‬ ‫‪19‬‬ ‫‪-‬‬ ‫كوفيد‬ ‫(‬ ‫ل‬ ‫سلبية‬ ‫بنتيجة‬ ‫فحص‬ ‫للمالديف‬ ‫المسافرين‬ ‫جميع‬ ‫يلزم‬ ‫‪2020‬‬ ‫ب‬ ‫سبتم‬ ‫‪10‬‬ ‫من‬ ‫بتداءا‬ ‫إ‬ الرسائل‬ ‫تقبل‬ ‫وال‬ ‫ية‬ ‫االنجلب‬ ‫وباللغة‬ ‫مطبوعة‬ ‫الفحص‬ ‫نتيجة‬ ‫تكون‬ ‫ان‬ ‫يجب‬ ‫‪,‬‬ ‫شهرا‬ ‫‪12‬‬ ‫ال‬ ‫سن‬ ‫دون‬ ‫الرضع‬ ‫ذلك‬ ‫من‬ ‫ويعف‬ ‫اقىص‬ ‫بحد‬ ‫الجوال‪.‬‬ ‫عىل‬ ‫االشعارات‬ ‫أو‬ ‫‪.‬النصية‬</li>

                    <li>‫ف‬ ‫التأخب‬ ‫لتجنب‬ ‫ساعة‬ ‫‪24‬‬ ‫ب‬ ‫منها‬ ‫والمغادرة‬ ‫للمالديف‬ ‫الوصول‬ ‫قبل‬ ‫مسافر‬ ‫لكل‬ ‫هنا‬ ‫إضغط‬ ‫الصح‬ ‫اإلفصاح‬ ‫نموذج‬ ‫تعبئة‬ ‫يجب‬ السفر‪.‬‬ ‫اجراءات‬ </li>

                    <li>‫المنتجع‪.‬‬ ‫باسم‬ ‫او‬ ‫العميل‬ ‫باسم‬ ‫بلوحة‬ ‫بالمنتجع‬ ‫الخاص‬ ‫المندوب‬ ‫طريق‬ ‫عن‬ ‫يكون‬ ‫المطار‬ ‫ف‬ ‫االستقبال‬</li>

                    <li>‫الحجز‪.‬‬ ‫حسب‬ ‫بكم‬ ‫الخاصة‬ ‫النقل‬ ‫وسيلة‬ ‫اىل‬ ‫بأخذكم‬ ‫المندوب‬ ‫يقوم‬ ‫س‬</li>

                    <li>‫يد‪.‬‬ ‫شنطة‬ ‫كيلو‬ ‫‪3‬‬ ‫‪+‬‬ ‫شخص‬ ‫لكل‬ ‫كيلو‬ ‫‪20‬‬ ‫هو‬ ‫المائية‬ ‫الطائرة‬ ‫ف‬ ‫المسموح‬ ‫الوزن‬</li>



                    <li>‫يد‪.‬‬ ‫شنطة‬ ‫كيلو‬ ‫‪5‬‬ ‫‪+‬‬ ‫شخص‬ ‫لكل‬ ‫كيلو‬ ‫‪20‬‬ ‫هو‬ ‫الداخلية‬ ‫الرحلة‬ ‫ف‬ ‫المسموح‬ ‫الوزن‬</li>

                    <li>‫يد‪.‬‬ ‫شنطة‬ ‫كيلو‬ ‫‪5‬‬ ‫‪+‬‬ ‫شخص‬ ‫ل‬ ‫لك‬ ‫كيلو‬ ‫‪25‬‬ ‫هو‬ ‫ع‬ ‫الرسي‬ ‫القارب‬ ‫ف‬ ‫المسموح‬ ‫الوزن‬</li>

                    <li>‫‪‫‪.‬‬ ‫األمريك‬ ‫الدوالر‬ ‫ه‬ ‫المالديف‬ ‫مطار‬ ‫ف‬ ‫المستخدمة‬ ‫العملة‬</li>

                    <li>‫الوصول‪.‬‬ ‫عند‬ ‫المنتجع‬ ‫طريق‬ ‫عن‬ ‫وتكون‬ ‫السعر‬ ‫ف‬ ‫مشمولة‬ ‫غب‬ ‫البحرية‬ ‫األنشطة‬ ‫جميع‬</li>

                    <li>‫عرصا‪.‬‬ ‫‪3:30‬‬ ‫اىل‬ ‫صباحا‬ ‫‪8:30‬‬ ‫بي‬ ‫ما‬ ‫المائية‬ ‫الطائرة‬ ‫أوقات‬</li>

                    <li>‫االستقبال‪.‬‬ ‫عند‬ ‫المندوب‬ ‫من‬ ‫مساعدة‬ ‫بطلب‬ ‫المطار‬ ‫من‬ ‫يحة‬ ‫ش‬ ‫ر‬ ‫اء‬ ‫ش‬ ‫ر‬ ‫ويمكن‬ ‫مجانا‬ ‫فاي‬ ‫الواي‬ ‫توفر‬ ‫المنتجعات‬ ‫جميع‬</li>

                    <li>‫جعات‪.‬‬ ‫المنت‬ ‫ف‬ ‫كامل‬ ‫بشكل‬ ‫تعمل‬ ‫وجميعها‬ ‫)‬ ‫إئتمانية‬ ‫بطاقة‬ ‫–‬ ‫نقدا‬ ‫(‬ ‫ماليا‬ ‫المالديف‬ ‫ف‬ ‫التعامل‬ ‫يمكن‬</li>

                    <li>‫درجة‪.‬‬ ‫‪30‬‬ ‫‪-‬‬ ‫‪28‬‬ ‫بي‬ ‫معتدلة‬ ‫العام‬ ‫طوال‬ ‫المالديف‬ ‫ف‬ ‫الحرارة‬ ‫درجة‬</li>

                    <li>‫الجنسيات‪.‬‬ ‫لجميع‬ ‫مسبقة‬ ‫دخول‬ ‫ة‬ ‫تأشب‬ ‫اىل‬ ‫المالديف‬ ‫تحتاج‬ ‫ال‬</li>
                <ol/>
            </div>"""

        return result
    
    term_condition = fields.Html("General Instruction")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('tp.auto.sequence') or 'New'
        records = super(sale_order_customized, self).create(vals_list)
        for record in records:
            record._check_room_quantity()
            for hotel in record.hotel_pkg:
                hotel.update_summary_from_hotel()
        return records


    def write(self, vals):
        return super(sale_order_customized, self).write(vals)

    def set_to_validate(self):

        self.stages = 'validate'
        for hotel in self.hotel_pkg:
            hotel.update_summary_from_hotel()


    def send_thankyou_sms(self):


        current_date = fields.Date.today()
        thanks_day = current_date - dt.timedelta(days=1)
        sale_order = self.env['reservation.order'].search([('stages','=','validate'),('departure_date','=',thanks_day)])
        # ,('id','=',1792)
        for x in sale_order:
            # sms_text = ' '
            if x.company_id.custom_thank_you:
                sms_text = x.company_id.custom_thank_you + '. \n  SMS ID: %s'%sale_order.id
            else:
                sms_text = "الحمدلله على السلامة ، فريق رونق سعيد بخدمتكم و نتمنى منكم تقييم خداماتنا على قوقل أو أحد وسائل التواصل الإجتماعي \n https://goo.gl/maps/yGYXfGDjoDJ5a89G8" + '. \n  SMS ID: %s'%sale_order.id 
            if x.partner_id.phone:
                mobile = x.partner_id.phone
            if not x.partner_id.phone:
                mobile = x.partner_id.mobile
            self.send_thankyou_sms_function(mobile,sms_text)

    # def send_thankyou_sms_function(self,mobile,sms_text):

        sms_text_new = str(sms_text)+ '\n' + '.' 
        time_to_send_sms=""
        values = """
        {
            "userName": "rawnaqtourism",
            "numbers": "%s",
            "userSender": "RAWNAQ",
            "apiKey": "61f0216ff366d565a4fd46f01aeb53a7",
            "msg": "%s",
            "timeToSend": "%s",
            "exactTime": "%s"
        } """ % (mobile,sms_text_new, time_to_send_sms, time_to_send_sms)
    
        response = requests.post('https://www.msegat.com/gw/sendsms.php', data=values.encode('utf-8'))
        resp = response.json()

        print(values.encode('UTF-8'))
        code = resp['code']
        resp['code']
        if response.status_code == 200:
            if resp['code']=='1':
                return {'warning': 'SMS Sent Successfully!'}
            else:
                error_msg_dict = {
                'M0000': 'Success',
                'M0001' : 'Variables missing',
                'M0002' : 'Invalid login info',
                'M0022' : 'Exceed number of senders allowed',
                'M0023' : 'Sender Name is active or under activation or refused',
                'M0024' : 'Sender Name should be in English or number',
                'M0025' : 'Invalid Sender Name Length',
                'M0026' : 'Sender Name is already activated or not found',
                'M0027' : 'Activation Code is not Correct',
                '1010' : 'Variables missing',
                '1020' : 'Invalid login info',
                '1050' : 'MSG body is empty',
                '1060' : 'Balance is not enough',
                '1061' : 'MSG duplicated',
                '1110' : 'Sender name is missing or incorrect',
                '1120' : 'Mobile numbers is not correct',
                '1140' : 'MSG length is too long',
                'M0029' : 'Invalid Sender Name - Sender Name should contain only letters, numbers and the maximum length should be 11 characters',
                'M0030' : 'Sender Name should ended with AD',
                'M0031' : 'Maximum allowed size of uploaded file is 5 MB',
                'M0032' : 'Only pdf,png,jpg and jpeg files are allowed!',
                'M0033' : 'Sender Type should be normal or whitelist only',
                'M0034' : 'Please Use POST Method',
                }

                raise ValidationError("SMS sending failed. "+ error_msg_dict[code])

    def set_to_draft(self):

        self.stages= 'draft'

    @api.onchange('get_term_conditions')
    def get_term_conditions_all(self):

        if self.get_term_conditions:
            self.flights_cancel_policy = self.get_term_conditions.flights_cancel_policy
            self.hotels_cancel_policy = self.get_term_conditions.hotels_cancel_policy
            self.transfers_cancel_policy = self.get_term_conditions.transfers_cancel_policy
            self.tours_cancel_policy = self.get_term_conditions.tours_cancel_policy
            self.visa_cancel_policy = self.get_term_conditions.visa_cancel_policy
            self.packages_cancel_policy = self.get_term_conditions.packages_cancel_policy
            self.private_jet_cancel_policy = self.get_term_conditions.private_jet_cancel_policy
            self.yacht_cancel_policy = self.get_term_conditions.yacht_cancel_policy
            self.cruise_cancel_policy = self.get_term_conditions.cruise_cancel_policy
            self.other_cancel_policy = self.get_term_conditions.other_cancel_policy
            self.term_condition = self.get_term_conditions.voucher_cancel_policy
        if not self.get_term_conditions:
            self.flights_cancel_policy = False
            self.hotels_cancel_policy = False
            self.transfers_cancel_policy = False
            self.tours_cancel_policy = False
            self.visa_cancel_policy = False
            self.packages_cancel_policy = False
            self.private_jet_cancel_policy = False
            self.yacht_cancel_policy = False
            self.cruise_cancel_policy = False
            self.other_cancel_policy = False
            self.term_condition = False


    @api.depends('partner_id')
    def _get_guest_info_m2m(self):
        for rec in self:
            rec.partner_id_mtom = False
            if rec.partner_id:
                rec.job_of_company = rec.partner_id.job_of_company
                liste = [rec.partner_id.id]
                for sub in rec.partner_id.sub_customer:
                    if sub.customer_name:
                        liste.append(sub.customer_name.id)
                rec.partner_id_mtom = [(6, 0, list(set(liste)))]
   
    @api.onchange('partner_id')
    def black_list_warning(self):

        if self.partner_id:
            if self.partner_id.blacklist:
                return {'value':{},'warning':{'title':
                        'warning','message':"This is a blacklist customer."}}

    def get_family_info(self):

        for x in self.passenger_pkg:
            x.unlink()

        family_list = []
        for x in self.partner_id.sub_customer:
            rec = self.env['passenger.pkg'].create({
                'name':x.customer_name.id,
                'age':x.age,
                'nationality_of_client':x.nationality_of_client.id,
                'passenger_return':self.id,
                })

    def _compute_count_func(self):
        for rec in self:
            rec.rec_count = self.env['account.move'].search_count([('invoice_origin', 'like', rec.name),('move_type','=','in_invoice')])
            rec.vendor_credits_count = self.env['account.move'].search_count([('invoice_origin', 'like', rec.name),('move_type','=','in_refund')])
    
    def _compute_count_func_inv(self):
        move_obj = self.env['account.move']
        for rec in self:
            rec.rec_count_inv = move_obj.search_count([('package_no', 'like', rec.name),('move_type', '=', 'out_invoice')])
            rec.cust_credits_count = move_obj.search_count([('package_no', '=', rec.name),('move_type', '=', 'out_refund')])

    def view_rec(self):
        return {
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'name':'Vendor Bills',
            'view_type': 'form',
            'target': 'current',
            'domain': [('invoice_origin','like',self.name),('move_type','=','in_invoice')],
            }

    def view_cust_note_rec(self):
        return {
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'name':'Customer Credit Notes',
            'view_type': 'form',
            'target': 'current',
            'domain': [('package_no','like',self.name),('move_type','=','out_refund')],
            }

    def view_vendor_note_rec(self):
        return {
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'name':'Vendor Credit Notes',
            'view_type': 'form',
            'target': 'current',
            'domain': [('invoice_origin','like',self.name),('move_type','=','in_refund')],
            }

    def view_rec_inv(self):
        return {
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'name':'Customer Invoice',
            'view_type': 'form',
            'target': 'current',
            'domain': [('package_no','like',self.name),('move_type','=','out_invoice')],
            }
    def prepare_invoice(self):

        journal = self.env['account.move'].with_context(force_company=self.company_id.id, default_type='out_invoice')._get_default_journal()
        invoice_vals = {
            'invoice_date': self.date_order,
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_origin': self.name,
            'invoice_line_ids': [],
        }

        return invoice_vals

    def update_the_server_tax_type(self):

        for summary in self.itinarnay_package:
            if summary.service_type=='flight':
                if self.flights_pkg:
                    for flight in self.flights_pkg:
                        summary.service_tax_type = flight.service_tax_type

            if summary.service_type=='hotel':
                if self.hotel_pkg:

                    for hotel in self.hotel_pkg:
                        summary.service_tax_type = hotel.service_tax_type

            if summary.service_type=='transfer':
                if self.transportation_pkg:
                    for trans in self.transportation_pkg:
                        summary.service_tax_type = trans.service_tax_type
            if summary.service_type=='tours':
                if self.tours_pkg:
                    for tour in self.tours_pkg:
                        summary.service_tax_type = tour.service_tax_type
            if summary.service_type=='visa':
                if self.visa_pkg:
                    for visa in self.visa_pkg:
                        summary.service_tax_type = visa.service_tax_type
            if summary.service_type=='ready_package':
                if self.packages_pkg:
                    for package in self.packages_pkg:
                        summary.service_tax_type = package.service_tax_type

            if summary.service_type=='private_jet':
                if self.privatejet_pkg:
                    for private in self.privatejet_pkg:
                        summary.service_tax_type = private.service_tax_type
            if summary.service_type=='yacht':
                if self.yacht_pkg:
                    for yacht in self.yacht_pkg:
                        summary.service_tax_type = yacht.service_tax_type
            if summary.service_type=='cruise':    
                if self.cruises_pkg:
                    for cruise in self.cruises_pkg:
                        summary.service_tax_type = cruise.service_tax_type
            if summary.service_type=='other': 
                if self.otherservices_pkg:
                    for other in self.otherservices_pkg:
                        summary.service_tax_type = other.service_tax_type

    def create_invoice(self):

        self.create_invoice_func('out_invoice')
        self.update_the_server_tax_type()


    def create_invoice_func(self, invoice_type):
    
        existing_invoice = self.env['account.move'].search([
        ('invoice_origin', '=', self.name),
            ('move_type', '=', 'out_invoice'),   # Sale invoice
            ('state', '=', 'posted')
        ], limit=1)

        if existing_invoice:
            credit_notes = self.env['account.move'].search([
                ('reversed_entry_id', '=', existing_invoice.id),
                ('move_type', '=', 'out_refund'),   # credit note
                ('state', '=', 'posted')
            ], limit=1)

            if not credit_notes:
                raise ValidationError(
                    f"A posted invoice ({existing_invoice.name}) already exists for {self.name}. ""You must issue a credit note first for the original invoice before issuing a new invoice.")

        # --------------------------------------
        journal_id = self.env['account.journal'].search([('type','=','sale')],limit=1)

        partner = self.partner_id.id
        ref = ''
        if self.agent:
            partner = self.agent.id
            ref = self.partner_id.name

        grouped_lines = {}
        customer_invoice = []
        # this is new code for show service type in line section
        for line in self.itinarnay_package:
            price = line.price
            qty = line.no_of_person

            if line.amnt_fc and line.exchange_rate > 0:
                price = line.amnt_fc * line.exchange_rate

            if line.service_type == 'flight':
                total = (line.price * line.no_of_person) + line.commission
            else:
                total = (line.price) + line.commission
                qty = 1

            account_id = line.product_id.property_account_income_id or line.product_id.categ_id.property_account_income_categ_id
            if account_id and account_id.account_type in ('asset_receivable', 'liability_payable'):
                account_id = False

            if not account_id:
                company = self.company_id or self.env.company
                account_id = company.income_account_id

            if not account_id:
                account_id = self.env['account.account'].search([
                    ('sale', '=', True),
                    ('account_type', 'in', ['income', 'income_other']),
                ], limit=1)

            if not account_id:
                account_id = self.env['account.account'].search([
                    ('account_type', 'in', ['income', 'income_other']),
                ], limit=1)

            if not account_id:
                product_name = line.product_id.display_name or line.description or 'Service line'
                raise ValidationError(f"Please configure an Income Account for {product_name}.")

            tax_ids = []
            taxes = self.env['account.tax'].search([('service_tax_type', '=', line.service_tax_type),('type_tax_use', '=', 'sale'),('active', '=', True)])
            tax_ids = taxes.ids


            price_unit = line.commission + (price * qty)
            if invoice_type == 'out_refund':
                price_unit = -price_unit

            # if line.service_type not in grouped_lines:
            #     grouped_lines[line.service_type] = []
            customer_invoice.append((0, 0, {
                # 'display_type': 'product',
                'name': f"{line.description}, {self.name}",
                'quantity': 1,
                'airline': line.airline.id or False,
                'room_type': [(6, 0, line.room_type.ids)],
                'airline_pnr': line.airline_pnr,
                'e_ticket': line.e_ticket,
                'e_ticket_m2m': [(6, 0, line.e_ticket_m2m.ids)],
                'price_unit': price_unit,
                'price_unit_ecube': line.commission + (price * qty),
                'commission': line.commission,
                'date_from': line.date_from,
                'date_to': line.date_to,
                'package_line': line.id,
                'currency_fc': line.currency_name.id,
                'amnt_fc': line.amnt_fc,
                'account_id': account_id.id,
                'product_id': line.product_id.id,
                'journal_id': journal_id.id,
                'tax_ids': [(6, 0, tax_ids)],
            }))

        # line_ids = []
        # for service_type, lines in grouped_lines.items():
        #     # Pehle Section Line add karain
        #     line_ids.append((0, 0, {
        #         'display_type': 'line_section',
        #         'account_id': False,
        #         'name': dict(self.itinarnay_package._fields['service_type'].selection).get(service_type, 'Other'),
        #     }))
            
        #     line_ids.extend(lines)

        

        today = str(date.today())
        today = datetime.strptime(str(today), "%Y-%m-%d")
        if self.arrival_date:
            arrival_date = str(self.arrival_date)
            arrival_date = datetime.strptime(str(arrival_date), "%Y-%m-%d")
            date_difference = arrival_date - today
            if date_difference.days >= 21:
                # date_1 = datetime.strptime(self.arrival_date, "%Y/%m/%d")
                date_1 = arrival_date

                due_date = date_1 - dt.timedelta(days=21)
            else:
                due_date = today
        else:
            due_date = today

        if not customer_invoice:
            raise ValidationError("No summary/service lines found to create invoice.")

        invoice_vals = {
            # 'invoice_date': datetime.today(),
            'invoice_date': self.arrival_date,
            'move_type': invoice_type,
            'narration': self.company_id.invoice_terms or self.env.company.invoice_terms,
            'partner_id': partner,
            # 'invoice_payment_term_id': self.payment_term_id.id or False,
            'journal_id':journal_id.id,
            'payment_term': self.payment_term,
            'payment_date_custom': due_date,
            'invoice_date_due': due_date,
            'arrival_date': self.arrival_date,
            'departure_date': self.departure_date,
            'package_no': self.name,
            'ref': ref,
            'commissioned': self.commissioned,
            'invoice_origin': self.name,
            # 'account_id':account_id.id,
            'invoice_line_ids': customer_invoice,
        }
        # sudo ssh root@5.189.175.68
        
        move = self.env['account.move'].with_context(default_move_type=invoice_type).create(invoice_vals)
        # move.get_address()


    # def prepare_bill(self,vendor):
    #     invoice_vals = {
    #         'invoice_date':self.date_order,
    #         'move_type': 'in_invoice',
    #         'partner_id': vendor,
    #         'invoice_origin': self.name,
    #         # 'currency_id' :False,
    #         'ref':'('+self.partner_id.name+')'+self.name,
    #         'invoice_line_ids': [],
    #     }

    #     return invoice_vals



    @api.onchange('departure_date', 'arrival_date')
    def check_date_validation(self):
        if self.departure_date and self.arrival_date:
            if self.arrival_date > self.departure_date:
                # self.arrival_date = None
                raise ValidationError('Arrival date is greater than departure date.')


    @api.onchange('partner_id')
    def address_contact(self):

        if self.partner_id:
            self.invoice_add = "%s %s %s %s %s %s" %(self.partner_id.ind_street or '', self.partner_id.ind_street2 or '', self.partner_id.ind_city or '', self.partner_id.ind_state_id.name or '',self.partner_id.ind_zip or '',self.partner_id.ind_country_id.name or '')
            self.delivery_add = "%s %s %s %s %s %s" %(self.partner_id.ind_street or '', self.partner_id.ind_street2 or '', self.partner_id.ind_city or '', self.partner_id.ind_state_id.name or '',self.partner_id.ind_zip or '',self.partner_id.ind_country_id.name or '')

class UsdCurrency(models.Model):
    _name ='usd.currency'
    _description ="USD Currency"
    name = fields.Char("Currency Name")


class CityCodes(models.Model):
    _name = 'city.codes'
    _rec_name = 'city'
    _description = 'city Codes Model'

    code = fields.Char('Code')
    country = fields.Char('Country')
    city = fields.Char('City')

class FightClassForm(models.Model):
    _name = 'fight.class'
    _description ="Flight Class"

    name =fields.Char("Name")

class all_services(models.Model):
    _name = 'all.services'
    _description = "All Service"
    _order = "sequence"
    _rec_name = 'product_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Integer(string='Sequence', help="Gives the sequence order when displaying a list of analytic distribution")
    date_to =fields.Date("Date to")
    date_from =fields.Date("Date from")
    airline = fields.Many2one('res.partner',"Airline",domain="[('airline_supplier','=',True)]")
    supplier = fields.Many2one('res.partner',"Supplier")
    customer = fields.Many2one('res.partner',"Customer")
    customer_m2m = fields.Many2many('res.partner',string="Partner")
    from_to = fields.Char("From/To")
    from_loc = fields.Many2one('city.codes', "From")
    to_loc = fields.Many2one('city.codes', "To")
    flight = fields.Char(string='Flight')
    fight_class = fields.Many2one('fight.class',string='Class')
    departures = fields.Datetime("Departures Date")
    arrival = fields.Datetime("Return Date")
    e_ticket = fields.Char(string='E-Ticket')
    e_ticket_m2m = fields.Many2many('electronic.ticket', 'flight_eticket_pkg_rel',string='E-Tickets')
    # pnr_no = fields.Char(string='PNR #')
    bag = fields.Char(string='Bag')
    occasion = fields.Char(string='Occasion')
    special_remarks = fields.Char(string='Special Remarks')
    offered_applied = fields.Char(string='Applied Offer')
    rate = fields.Char(string='Rate')
    terminal = fields.Char(string='Terminal')
    airline_pnr = fields.Char(string='Airline PNR')
    no_of_person = fields.Float("No. of Guests ",default=1)
    price = fields.Float("Net Amount")
    amnt_fc = fields.Float("Net Amount FC")
    exchange_rate= fields.Float("Exchange Rate")
    commission= fields.Float("Commission")
    currency_name= fields.Many2one('res.currency', "Currency")
    total= fields.Float("Total")
    description = fields.Text("Description")
    amount = fields.Float("Net Amount")
    issue_date =fields.Date("Issue Date")

    product_id = fields.Many2one('product.product',"Product")
    hotel_id = fields.Many2one('res.partner',"Hotel")
    confirmation_no = fields.Char("Confirmation Number")
    pick_up_place = fields.Char("Pick Up")
    drop_of_place = fields.Char("Drop-off")
    date = fields.Datetime("Date" ,default=datetime.now().replace(hour=19, minute=0, second=0))
    transfer_type = fields.Many2one('transfer.type', string="Transfer Type")
    vehicle_type = fields.Many2one('vehicle.type', string="Vehicle Type")
    wait_time_policy = fields.Many2one('wait.time.policy', string="Waiting Time Policy")
    rent_car = fields.Char("Rent Car")
    hours = fields.Integer("Hours")

    room_occupancy=fields.Many2one('room.occupancy',"Room Occupancy")
    nights = fields.Integer("Nights")
    room_qty = fields.Integer("Room Quantity")
    room_type=fields.Many2many('room.type', 'room_type_service_rel', string="Room Type")
    transfer= fields.Many2many('hotel.transfer', 'transfer_service_rel',string="Transfer")
    meal_plan= fields.Many2one('meal.plan', string="Meal Plan")
    hotel_meal_plan = fields.Many2many('meal.plan', 'meal_plan_service_rel', string="Meal Plans")
    ticket_day = fields.Many2one('days.name',"Ticket Day")
    guided_or_not = fields.Selection([('guided', 'Guided'),
    ('not_guided', 'Not Guided'),
    ],string='Guided/Not Guided')
    # ticket_price = fields.Float("Net Amount")

    visa_status = fields.Selection([('draft', 'Requested Documents'),
    ('recieved', 'Recieved Documents'),
    ('incomplete', 'Incomplete Documents')],string='Visa Status')

    category = fields.Selection([('infant', 'Infant'),
    ('child', 'Child'),
    ('adult', 'Adult')],string='Guest Category', related='customer.category')
    validity = fields.Char("Validity (Start/Expire)")
    no_of_nights = fields.Integer("No of Nights")
    rooms_type = fields.Char("Rooms Type")
    transfer_mode = fields.Char("Transfer Mode")
    guest_no = fields.Float("Guest No")
    added_values = fields.Char("Added Values")
    product_type = fields.Char("Product Type")
    days_valid = fields.Many2one('days.name',"Days Valid")

    duration = fields.Float(string="Duration")
    yacht_type = fields.Many2one("yacht.type", string='Yacht Type')
    departure_place = fields.Char(string="Departure Place")
    occupancy = fields.Char(string="Occupancy")
    arrival_place = fields.Char(string="Arrival Place")
    cabin_type = fields.Many2one("cabin.type", string='Cabin Type')
    bill_id = fields.Many2one('account.move', "Vendor Bill")

    service_type = fields.Selection([
        ('flight', 'Flight'),
        ('hotel', 'Hotel'),
        ('transfer', 'Transfer'),
        ('tours', 'Tours'),
        ('visa', 'Visa'),
        ('ready_package', 'Ready Package'),
        ('private_jet', 'Private Jet'),
        ('yacht', 'Yacht'),
        ('cruise', 'Cruise'),
        ('other', 'Other'),
        ],string='Service Type')

    services_return = fields.Many2one('reservation.order')
    flights_return = fields.Many2one('reservation.order')
    package_return = fields.Many2one('reservation.order')
    yacht_return = fields.Many2one('reservation.order')
    cruises_return = fields.Many2one('reservation.order')
    privatejet_return = fields.Many2one('reservation.order')
    otherservices_return = fields.Many2one('reservation.order')
    tours_return = fields.Many2one('reservation.order')
    itinarnay_return = fields.Many2one('reservation.order')
    transportation_return = fields.Many2one('reservation.order')
    hotel_return = fields.Many2one('reservation.order')
    visa_return = fields.Many2one('reservation.order')
    all_old_hotel_record = fields.Many2one('all.services',string="All hotel record", help="This field is add for summry link with hotel")

    confirmed_date_email = fields.Date(string="Confirmed Date", readonly=True)
    drop_off_date = fields.Date(string="Drop-Off Date")
    free_space_time = fields.Char(string="Free Time Space")

    commission_able = fields.Boolean(string="Commissionable")
    fell_date = fields.Date(string="Fell Date")
    service_tax_type = fields.Selection([
        ('international','International'),
        ('domestic','Domestic'),
        ],tracking=True, string="Service Tax Type")


    def duplicate_line(self):
        self.copy({'hotel_return': self.hotel_return.id})

    @api.onchange('departures', 'arrival')
    def get_the_date_from_and_to(self):
        if self.flights_return:
            if self.departures:
                self.date_from = self.departures.date()
            else:
                self.date_from = False

            if self.arrival:
                self.date_to = self.arrival.date()
            else:
                self.date_to = False

    @api.onchange('departures', 'arrival', 'privatejet_return')
    def get_private_jet_dates(self):
        if self.privatejet_return:
            if self.departures:
                self.date_from = self.departures
            if self.arrival:
                self.date_to = self.arrival

    # def unlink(self):
    #     for record in self:
    #         if record.all_old_hotel_record:
    #             record.all_old_hotel_record.unlink()

    #     return super(all_services, self).unlink()


    def get_guests(self):
        guests_names = ""
        if self.customer_m2m:
            customer_m2m = sorted(self.customer_m2m,)
            for x in customer_m2m:
                if x.category:
                        guests_names += str(x.name )+'('+str(x.category).capitalize()+"), "
                else:
                    guests_names += str(x.name )+", "
            if len(guests_names) >2:
                guests_names = guests_names[:-2]
        return guests_names

    def get_no_of_person(self):
        main_value = ''
        if self.customer_m2m:
            infant = 0
            child = 0
            adult = 0
            for x in self.customer_m2m:
                if x.category:
                    if x.category == 'infant':
                        infant += 1
                    if x.category == 'child':
                        child += 1
                    if x.category == 'adult':
                        adult += 1
            value_1 = ''
            value_2 = ''
            value_3 = ''


            if infant > 1:
                value_1 = str(infant) + ' Infants' +  ' ' 
            if infant <= 1 and infant > 0:
                value_1 = str(infant) + ' Infant' +  ' ' 

            if child > 1:
                value_2 = str(child) + ' Children' +  ' '

            if child <= 1 and child > 0:
                value_2 = str(child) + ' Child' +  ' '
            if adult > 1:
                value_3 = str(adult) + ' Adults' +  ' '

            if adult <= 1 and adult > 0:
                value_3 = str(adult) + ' Adult' +  ' '
            
            if value_1:
                main_value = value_1
            if value_2:
                main_value = value_2
            if value_3:
                main_value = value_3
            if value_1 and value_2:
                main_value = value_2+ ',' + value_1
            if value_1 and value_3:
                main_value = value_3 + ',' + value_1
            if value_2 and value_3:
                main_value = value_3 + ',' + value_2
            if value_1 and value_2 and value_3:
                main_value = value_3 + ',' + value_2 + ',' + value_1
        return main_value


    def get_rooms(self):
        rooms_names = ""
        if self.room_type:
            for x in self.room_type:
                rooms_names += x.name+", "
            if len(rooms_names) >2:
                rooms_names = rooms_names[:-2]
        return rooms_names

    def get_meals(self):
        meal_names = ""
        if self.hotel_meal_plan:
            for x in self.hotel_meal_plan:
                meal_names += x.name+", "
            if len(meal_names) >2:
                meal_names = meal_names[:-2]
        return meal_names
    def get_transfers(self):
        transfer_names = ""
        if self.transfer:
            for x in self.transfer:
                transfer_names += x.name+", "
            if len(transfer_names) >2:
                transfer_names = transfer_names[:-2]
        return transfer_names

    def get_hotels_now_e(self):
        self.ensure_one()
        if not self.hotel_return or not self.supplier:
            return self

        same_supplier_ids = self.hotel_return.hotel_pkg.filtered(
            lambda service: service.supplier == self.supplier
        ).mapped('supplier').ids
        if same_supplier_ids:
            return self.env['all.services'].search([
                ('hotel_return', '=', self.hotel_return.id),
                ('supplier', 'in', same_supplier_ids),
            ])
        return self

    def action_hotel_email_sent(self):

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            if self.hotel_return.reservation_type == 'b2c':
                template_id = ir_model_data._xmlid_lookup('travel_package.new_package_hotels_email_template')[1]
            else:
                template_id = ir_model_data._xmlid_lookup('travel_package.new_package_hotels_email_template_without_welcome_letter')[1]
        except ValueError:
            template_id = False

        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False

        data_ids = []
        if self.hotel_return.reservation_type == 'b2c':

            for get in self.get_hotels_now_e():
                report_template_id = self.env['ir.actions.report'].sudo()._render_qweb_pdf('welcome_letter_report.welcome_letter_report_id',get.ids)
                data_record = base64.b64encode(report_template_id[0])
                ir_values = {
                'name': "Welcome Letter - {0}.pdf".format(get.hotel_return.partner_id.name),
                'type': 'binary',
                'datas': data_record,
                'store_fname': data_record,
                'mimetype': 'application/pdf',
                }
                data_id = self.env['ir.attachment'].create(ir_values)
                data_ids.append(data_id.id)
       
        ctx = {
           'default_model': 'all.services',
           'default_res_ids': self.ids,
           'default_template_id': template_id,
           'mail_notify_author': False,
           'notify_author': False,
           'default_notify_author': False,
           'default_mail_notify_author': False,
           'default_composition_mode': 'comment',
           'default_attachment_ids': [(6, 0, data_ids)]
        }
        return {
           'name': _('Hotel Email'),
           'type': 'ir.actions.act_window',
           'view_mode': 'form',
           'res_model': 'mail.compose.message',
           'views': [(compose_form_id, 'form')],
           'view_id': compose_form_id,
           'target': 'new',
           'context': ctx,
        }
    
    @api.model_create_multi
    def create(self, vals_list):
        new_recs = super(all_services, self).create(vals_list)
        for new_rec in new_recs:
            new_rec.check_date_validation()
            # new_rec.check_date_fromto_validation()
            new_rec.age_categ_change_validation()
            new_rec.get_the_date_from_and_to()
            new_rec.get_summery()
        return new_recs

    def write(self,vals):
        new_rec =super(all_services, self).write(vals)
        previous_date = self.departures
        arrival_date =self.arrival
        if 'departures' in vals or 'arrival' in vals:
            self.check_date_validation()
            self.age_categ_change_validation()
        if 'hotel_return' in vals or 'stages' in vals:
            self.update_summary_from_hotel()
        # self.check_date_fromto_validation()
        if self.flights_return.stages == 'validate':
            if previous_date>self.departures:
                raise ValidationError("You can not select a previous Date")
            if arrival_date > self.arrival or  arrival_date < self.arrival:

                raise ValidationError("You can not change Return Date")

        if 'privatejet_return' in vals or 'departures' in vals or 'arrival' in vals:
            self.get_private_jet_dates()
        if 'flights_return' in vals or 'departures' in vals or 'arrival' in vals:
            self.get_the_date_from_and_to()
        return True



    @api.onchange('departures', 'arrival')
    def age_categ_change_validation(self):
        if self.flights_return:
            if self.arrival and self.customer:
                if self.customer.dob:
                    temp = str(self.arrival)
                    temp_date = dateutil.parser.parse(temp).date()
                    year = (temp_date - self.customer.dob) // timedelta(days=365.2425)
                    nofmonths=  self.arrival.month - self.customer.dob.month
                    if nofmonths < 0: # if statement in case the current month is less than the birth minth
                        nofmonths = 12 + nofmonths
                    if nofmonths == 0:
                        year += 1
                    previous_categ = self.customer.category
                    current_categ = ""

                    if year > 12:
                        current_categ = 'adult'
                    elif year <=12 and year >= 2:
                        current_categ = 'child'
                    else:
                        current_categ = 'infant'

                    if current_categ != previous_categ:
                        res= {'warning':{'title':'warning','message':"Age Category of customer changes between departure or return date."}}
                        return res

    def prepare_invoice_line(self):
        if self.itinarnay_return:
            self.ensure_one()
            name=""
            if self.description and self.service_type:
                name = self.description + dict(self._fields['service_type'].selection).get(self.service_type)
            elif self.description:
                name = self.description
            else:
                name = dict(self._fields['service_type'].selection).get(self.service_type)
            
            if not self.product_id.property_account_income_id:
                account_id = self.env['account.account'].search([('name','=','Account Receivable')])
            if self.product_id.property_account_income_id:
                account_id = self.product_id.property_account_income_id
            count = 0
            for x in self.customer_m2m:
                count += 1
            qty = self.no_of_person * count
            return {
                'product_id': self.product_id.id,
                'name': name,
                'account_id': account_id.id,
                'quantity': qty,
                'price_unit_ecube': self.price,
                'price_unit': self.price,
                'commission': self.commission,
                'price_subtotal': self.total,
                'display_type': self.display_type,
                'sale_line_ids': [(4, self.id)],
        }

    def prepare_bill_line(self,supplier_id):
    
        if self.itinarnay_return:
            self.ensure_one()
            name=""
            if self.description and self.service_type:
                name = self.description + dict(self._fields['service_type'].selection).get(self.service_type)
            elif self.description:
                name = self.description
            else:
                name = dict(self._fields['service_type'].selection).get(self.service_type)
            if not self.product_id.property_account_income_id:
                account_id = self.env['account.account'].search([('name','=','Account Receivable')])
            if self.product_id.property_account_income_id:
                account_id = self.product_id.property_account_income_id

            return {
                'product_id': self.product_id.id,
                'name': name,
                'quantity': self.no_of_person,
                'price_unit': self.price,
                'account_id': account_id.id,
                # 'commission': self.commission,
                'price_subtotal': self.total,
                }
    
    @api.onchange('departures', 'arrival')
    def check_date_validation(self):
        if self.departures and self.arrival:
            if self.departures > self.arrival:
                raise  ValidationError('Departure date is great than return date.')

    @api.onchange('date_from', 'date_to')
    def check_date_fromto_validation(self):
        if self.date_from:
            current = date.today()
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                print ("uncomment the above line once the working is done")
            elif self.hotel_return:
                d1 = self.date_from
                d2 = self.date_to
                day = (d2 - d1).days # calculates the difference of days
                # for rec in self:
                self.nights = day

    @api.onchange('no_of_person','price','commission','exchange_rate','amnt_fc')
    def cal_subtotal(self):
        count = 0
        for x in self.customer_m2m:
            count += 1
        vals={}
        qty = self.no_of_person * count
        if self.amnt_fc and self.exchange_rate:
            vals['price'] = self.amnt_fc*self.exchange_rate
        print ("check 4")
        if self.service_type == 'flight':
            vals['total'] = (self.price * self.no_of_person) + self.commission
        else:
            vals['total'] = (self.price) + self.commission
        self.update(vals)


    @api.onchange('total','price','no_of_person')
    def get_commission(self):
        vals = {}
        if self.total and self.price:
            if self.service_type == 'flight':
                vals['commission']= self.total - (self.price*self.no_of_person)
            else:
                vals['commission']= self.total - self.price
            
        else:
            vals['commission']= 0
        self.update(vals)

    def update_summary_from_hotel(self):
        if self.hotel_return:
            liste_new = []
            if self.customer_m2m:
                for x in self.customer_m2m:
                    liste_new.append(x.id)

            room_liste_new = []
            if self.room_type:
                for x in self.room_type:
                    room_liste_new.append(x.id)

            meal_liste_new = []
            if self.hotel_meal_plan:
                for x in self.hotel_meal_plan:
                    meal_liste_new.append(x.id)

            transfer_liste_new = []
            if self.transfer:
                for x in self.transfer:
                    transfer_liste_new.append(x.id)

            self.all_old_hotel_record.product_id = self.product_id.id
            self.all_old_hotel_record.service_type = 'hotel'
            self.all_old_hotel_record.customer_m2m = [(6,0,liste_new)]
            self.all_old_hotel_record.supplier = self.supplier.id
            self.all_old_hotel_record.description = 'Hotel'
            self.all_old_hotel_record.date_from = self.date_from
            self.all_old_hotel_record.date_to = self.date_to
            self.all_old_hotel_record.price = self.price
            self.all_old_hotel_record.commission = self.commission
            # self.all_old_hotel_record.all_old_hotel_record = self.id
            self.all_old_hotel_record.total = self.total
            self.all_old_hotel_record.itinarnay_return = self.hotel_return.id
            
            # Extra field add from Hotel to summary
            self.all_old_hotel_record.hotel_id = self.hotel_id.id
            self.all_old_hotel_record.customer = self.customer.id
            self.all_old_hotel_record.confirmation_no = self.confirmation_no
            self.all_old_hotel_record.room_occupancy = self.room_occupancy
            self.all_old_hotel_record.nights = self.nights
            self.all_old_hotel_record.room_type = [(6,0,room_liste_new)]
            self.all_old_hotel_record.room_qty = self.room_qty
            self.all_old_hotel_record.hotel_meal_plan = [(6,0,meal_liste_new)]
            self.all_old_hotel_record.no_of_person = self.no_of_person
            self.all_old_hotel_record.transfer = [(6,0,transfer_liste_new)]
            self.all_old_hotel_record.amnt_fc = self.amnt_fc
            self.all_old_hotel_record.currency_name = self.currency_name.id
            self.all_old_hotel_record.occasion = self.occasion
            self.all_old_hotel_record.special_remarks = self.special_remarks
            self.all_old_hotel_record.offered_applied = self.offered_applied
            self.all_old_hotel_record.rate = self.rate
            self.all_old_hotel_record.exchange_rate = self.exchange_rate

    def get_summery(self):
        if self.flights_return:
            self.itinarnay_return=self.flights_return.id
            self.service_type='flight'
            self.description='Flight'

        if self.hotel_return:
            liste_new = []
            if self.customer_m2m:
                for x in self.customer_m2m:
                    liste_new.append(x.id)

            room_liste_new = []
            if self.room_type:
                for x in self.room_type:
                    room_liste_new.append(x.id)

            meal_liste_new = []
            if self.hotel_meal_plan:
                for x in self.hotel_meal_plan:
                    meal_liste_new.append(x.id)

            transfer_liste_new = []
            if self.transfer:
                for x in self.transfer:
                    transfer_liste_new.append(x.id)


            create_record = self.env['all.services'].create({
                'product_id':self.product_id.id,
                'service_type':'hotel',
                'customer_m2m':[(6,0,liste_new)],
                'supplier':self.supplier.id,
                'description':'Hotel',
                'date_from':self.date_from,
                'date_to':self.date_to,
                'price':self.price,
                'commission':self.commission,
                'service_tax_type':self.service_tax_type,
                # 'all_old_hotel_record':self.id,
                'total':self.total,
                'itinarnay_return':self.hotel_return.id,
                
                # Extra field add from Hotel to summary
                'hotel_id':self.hotel_id.id,
                'customer':self.customer.id,
                'confirmation_no':self.confirmation_no,
                'room_occupancy':self.room_occupancy,
                'nights':self.nights,
                'room_type':[(6,0,room_liste_new)],
                'room_qty':self.room_qty,
                'hotel_meal_plan':[(6,0,meal_liste_new)],
                'no_of_person':self.no_of_person,
                'transfer':[(6,0,transfer_liste_new)],
                'amnt_fc':self.amnt_fc,
                'currency_name':self.currency_name.id,
                'occasion':self.occasion,
                'special_remarks':self.special_remarks,
                'offered_applied':self.offered_applied,
                'rate':self.rate,
                'exchange_rate':self.exchange_rate,
                })

            self.all_old_hotel_record = create_record.id
    
        if self.yacht_return:
            self.itinarnay_return=self.yacht_return.id
            self.service_type='yacht'
            self.description='Yacht'
    

        if self.visa_return:
            self.itinarnay_return=self.visa_return.id
            self.service_type='visa'
            self.description='Visa'
    

        if self.cruises_return:
            self.itinarnay_return=self.cruises_return.id
            self.service_type='cruise'
            self.description='Cruise'
    

        if self.transportation_return:
            self.itinarnay_return=self.transportation_return.id
            self.service_type='transfer'
            self.description='Transfer'

        if self.privatejet_return:
            self.itinarnay_return=self.privatejet_return.id
            self.service_type='private_jet'
            self.description='Private Jet'
    
        if self.tours_return:
            self.itinarnay_return=self.tours_return.id
            self.service_type='tours'
            self.description='Tours'

        if self.otherservices_return:
            self.itinarnay_return=self.otherservices_return.id
            self.service_type='other'
            self.description=self.description 
            # self.description='Other'

        if self.package_return:
            self.itinarnay_return=self.package_return.id
            self.service_type='ready_package'
            self.description='Ready Package'
                

    @api.onchange('currency_name')
    def get_currency_rate(self):
        if self.currency_name:
            self.exchange_rate = self._get_currency_exchange_rate()
        if not self.currency_name:
            self.exchange_rate = 0

    def _get_exchange_rate_date(self):
        self.ensure_one()
        order = (
            self.flights_return or
            self.hotel_return or
            self.transportation_return or
            self.tours_return or
            self.visa_return or
            self.package_return or
            self.privatejet_return or
            self.yacht_return or
            self.cruises_return or
            self.otherservices_return or
            self.itinarnay_return or
            self.services_return
        )
        return fields.Date.to_date(order.date_order) if order and order.date_order else fields.Date.context_today(self)

    def _get_currency_exchange_rate(self):
        self.ensure_one()
        if not self.currency_name:
            return 0.0
        return self.currency_name.with_context(date=self._get_exchange_rate_date()).rate

    @api.onchange('product_id')
    def get_detail(self):
        if self.package_return:
            self.validity = self.product_id.validity or None
            self.no_of_nights = self.product_id.no_of_nights or None
            self.transfer_mode = self.product_id.transfer_mode or None
            self.added_values = self.product_id.added_values or None
            self.price = self.product_id.rate or None
            self.product_type = self.product_id.product_type or None
            self.meal_plan = self.product_id.meal_plan.id

            room_type_ids = []
            for x in self.product_id.room_type:
                room_type_ids.append(x.id)
            self.update({
                'hotel_meal_plan':[(6,0,[self.product_id.meal_plan.id])],
                'room_type':[(6,0,room_type_ids)],
                })

    def create_bill_of_vendor(self):
        self.create_bill_of_vendor_func('in_invoice')

    def create_bill_of_vendor_func(self, invoice_type):
        if invoice_type == 'in_invoice':
            vendor_bill = self.env['account.move'].sudo().search([('state','in',['draft','posted']),('partner_id','=',self.supplier.id),('move_type','=',"in_invoice"),('package_no','like',self.itinarnay_return.name)])
            if vendor_bill:
                for x in vendor_bill:
                    if x.state == 'posted':
                        x.button_draft()
                        x.button_cancel()
                    if x.state == 'draft':
                        # x.button_draft()
                        x.button_cancel()
            if self.bill_id:
                credit_notes = self.env['account.move'].search([('move_type','=',"in_refund"),('ref','like',self.bill_id.name)])
                if not credit_notes:
                    if self.bill_id.state == 'draft':
                        self.bill_id.unlink()
                    else:
                        if self.bill_id.state == 'posted':
                            self.bill_id.button_draft()
                            self.bill_id.button_cancel()
                        if self.bill_id.state == 'draft':
                            self.bill_id.button_cancel()
                self.bill_id = False


        # ---------------------------------
        journal_id = self.env['account.journal'].search([('type','=','purchase')],limit=1)
        # for j in uniq_vendors:

        service_lines = self.env['all.services'].search([('supplier','=',self.supplier.id),('itinarnay_return','=',self.itinarnay_return.id)])
        company = self.itinarnay_return.company_id or self.env.company

        line_ids = []
        for line in service_lines:
            # --------------------------------------
            price = line.price
            qty = line.no_of_person
            if line.amnt_fc:
                if line.exchange_rate:
                    price = line.amnt_fc*line.exchange_rate
                else:
                    price = line.price


            if line.service_type == 'flight':
                total= (line.price * line.no_of_person) + line.commission
            else:
                total= (line.price)
                qty = 1

            if line.product_id:
                product = line.product_id.id


            account_id = line.product_id.property_account_expense_id or line.product_id.categ_id.property_account_expense_categ_id
            if account_id and account_id.account_type in ('asset_receivable', 'liability_payable'):
                account_id = False

            if not account_id:
                account_id = company.expense_account_id

            if not account_id:
                account_id = self.env['account.account'].search([
                    ('purchase', '=', True),
                    ('account_type', 'in', ['expense', 'expense_direct_cost']),
                ], limit=1)

            if not account_id:
                account_id = self.env['account.account'].search([
                    ('account_type', 'in', ['expense', 'expense_direct_cost']),
                ], limit=1)

            if not account_id:
                product_name = line.product_id.display_name or line.description or 'Service line'
                raise ValidationError(f"Please configure an Expense Account for {product_name}.")

            if invoice_type == 'in_refund':
                price = -price

            tax_ids = []
            taxes = self.env['account.tax'].search([('service_tax_type', '=', line.service_tax_type),('type_tax_use', '=', 'purchase'),('active', '=', True)])
            tax_ids = taxes.ids
            
            line_ids.append(
                (0,0, {
                    # 'name':str(line.description)+", "+str(line.itinarnay_return.name),
                    'name':(str(line.description) + ", ") if line.description else "" + str(line.itinarnay_return.name),
                    # 'quantity':line.itinarnay_return.no_of_particpents,
                    'quantity':qty,
                    'airline':line.airline.id,
                    'room_type':[(6,0,line.room_type.ids)],
                    'airline_pnr':line.airline_pnr,
                    'e_ticket':line.e_ticket,
                    'e_ticket_m2m':[(6,0,line.e_ticket_m2m.ids)],
                    'price_unit':price,
                    'price_unit_ecube':price,
                    'date_from':line.date_from,
                    'date_to':line.date_to,
                    'package_line':line.id,
                    'account_id':account_id.id,
                    'currency_fc':line.currency_name.id,
                    'amnt_fc':line.amnt_fc,
                    'product_id':line.product_id.id or None,
                    'journal_id':journal_id.id,
                    'tax_ids': [(6, 0, tax_ids)],
                    })
                )
        
        today = str(date.today())
        today = datetime.strptime(str(today), "%Y-%m-%d")
        if self.itinarnay_return.arrival_date:
            arrival_date = str(self.itinarnay_return.arrival_date)
            arrival_date = datetime.strptime(str(arrival_date), "%Y-%m-%d")
            date_difference = arrival_date - today
            if date_difference.days >= 3:
                # date_1 = datetime.strptime(self.itinarnay_return.arrival_date, "%Y/%m/%d")
                date_1 = arrival_date

                due_date = date_1 - dt.timedelta(days=3)
            else:
                due_date = today
        else:
            due_date = today

    
        if len(service_lines) == 1:
        
            invoice_vals = {
                'invoice_date': self.itinarnay_return.arrival_date,
                'move_type': invoice_type,
                'partner_id': self.supplier.id,
                'commissioned': self.itinarnay_return.commissioned,
                'invoice_origin': self.itinarnay_return.name,
                'payment_term': self.itinarnay_return.payment_term,
                'arrival_date': line.date_from,
                'departure_date': line.date_to,
                'payment_date_custom': due_date,
                'package_no': self.itinarnay_return.name,
                'journal_id': journal_id.id,
                'invoice_line_ids': line_ids,
            }
        else: 
            if service_lines:
                
                invoice_vals = {
                    'invoice_date': self.itinarnay_return.arrival_date,
                    'move_type': invoice_type,
                    'partner_id': self.supplier.id,
                    'commissioned': self.itinarnay_return.commissioned,
                    'invoice_origin': self.itinarnay_return.name,
                    # 'invoice_payment_term_id': self.itinarnay_return.payment_term_id.id or False,
                    'payment_term': self.itinarnay_return.payment_term,
                    'arrival_date': self.itinarnay_return.arrival_date,
                    'departure_date': self.itinarnay_return.departure_date,
                    'payment_date_custom': due_date,
                    'package_no': self.itinarnay_return.name,
                    'journal_id': journal_id.id,
                    'invoice_line_ids': line_ids,
                }
        move = self.env['account.move'].with_context(default_move_type=invoice_type).create(invoice_vals)


        for line in service_lines:
            line.bill_id = move.id
    def action_transfer_email_sent(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            if self.transportation_return.reservation_type == 'b2c':
                template_id = ir_model_data._xmlid_lookup('travel_package.package_transportation_email_template')[1]
            else:
                template_id = ir_model_data._xmlid_lookup('travel_package.package_transportation_email_template_without_welcome_letter')[1]
        except ValueError:
            template_id = False

        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        data_ids = []
        if self.transportation_return.reservation_type == 'b2c':

            for get in self.get_transfer_now_e():

                report_template_id = self.env['ir.actions.report'].sudo()._render_qweb_pdf('welcome_letter_report.welcome_letter_report_id',get.ids)
                # report_template_id = self.env.ref(
                #   'welcome_letter_report.welcome_letter_report_id')._render_qweb_pdf(get.id)
                data_record = base64.b64encode(report_template_id[0])
                ir_values = {
                'name': "Welcome Letter - {0}.pdf".format(get.transportation_return.partner_id.name),
                'type': 'binary',
                'datas': data_record,
                'store_fname': data_record,
                'mimetype': 'application/pdf',
                }
                data_id = self.env['ir.attachment'].create(ir_values)
                data_ids.append(data_id.id)
        ctx = {
           'default_model': 'all.services',
           'default_res_ids': self.ids,
           # 'default_use_template': bool(template_id),
           'default_template_id': template_id,
           'default_composition_mode': 'comment',
           'default_email_layout_xmlid': "mail.mail_notification_layout_with_responsible_signature",
           'default_attachment_ids': [(6, 0, data_ids)]
        }

        
        return {
           'name': _('Transfer Email'),
           'type': 'ir.actions.act_window',
           'view_mode': 'form',
           'res_model': 'mail.compose.message',
           'views': [(compose_form_id, 'form')],
           'view_id': compose_form_id,
           'target': 'new',
           'context': ctx,
        }

    def action_tour_email_sent(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            if self.tours_return.reservation_type == 'b2c':
                template_id = ir_model_data._xmlid_lookup('travel_package.package_tour_email_template')[1]
            else:
                template_id = ir_model_data._xmlid_lookup('travel_package.package_tours_email_template_without_welcome_letter')[1]
        except ValueError:
            template_id = False

        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False

        data_ids = []
        if self.tours_return.reservation_type == 'b2c':

            for get in self.get_tours_now_e():
                report_template_id = self.env['ir.actions.report'].sudo()._render_qweb_pdf('welcome_letter_report.welcome_letter_report_id',get.ids)
                data_record = base64.b64encode(report_template_id[0])
                ir_values = {
                'name': "Welcome Letter - {0}.pdf".format(get.tours_return.partner_id.name),
                'type': 'binary',
                'datas': data_record,
                'store_fname': data_record,
                'mimetype': 'application/pdf',
                }
                data_id = self.env['ir.attachment'].create(ir_values)
                data_ids.append(data_id.id)
       
        ctx = {
           'default_model': 'all.services',
           'default_res_ids': self.ids,
           'default_template_id': template_id,
           'default_composition_mode': 'comment',
           'default_email_layout_xmlid': "mail.mail_notification_layout_with_responsible_signature",
           'default_attachment_ids': [(6, 0, data_ids)]
        }
        return {
           'name': _('Tour Email'),
           'type': 'ir.actions.act_window',
           'view_mode': 'form',
           'res_model': 'mail.compose.message',
           'views': [(compose_form_id, 'form')],
           'view_id': compose_form_id,
           'target': 'new',
           'context': ctx,
        }

    def get_transfer_now_e(self):
        self.ensure_one()
        same_transfer = []

        for ho in self.transportation_return.transportation_pkg:
            if ho.supplier and self.supplier and ho.supplier.id == self.supplier.id:
                same_transfer.append(ho.supplier.id)

        if same_transfer and self.supplier and self.supplier.id in same_transfer:
            return self.env['all.services'].search([
                ('transportation_return', '=', self.transportation_return.id),
                ('supplier', 'in', same_transfer),
            ])
        return self

    def get_tours_now_e(self):
        self.ensure_one()
        same_tours = []

        for ho in self.tours_return.tours_pkg:
            if ho.supplier and self.supplier and ho.supplier.id == self.supplier.id:
                same_tours.append(ho.supplier.id)

        if same_tours and self.supplier and self.supplier.id in same_tours:
            return self.env['all.services'].search([
                ('tours_return', '=', self.tours_return.id),
                ('supplier', 'in', same_tours),
            ])
        return self

    def get_guests_others(self):
        guests_names = ""
        if self.customer_m2m:
            customer_m2m = sorted(self.customer_m2m,)
            for x in customer_m2m:
                if x.category:
                    print ("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCC")
                    print (dict(x._fields['category'].selection).get(x.type))
                    guests_names += str(x.name )+'('+str(x.category).capitalize()+"), "

                else:
                    guests_names += str(x.name )+", "
            if len(guests_names) >2:
                guests_names = guests_names[:-2]
        return guests_names

    def action_visa_email_sent(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            if self.visa_return.reservation_type == 'b2c':
                template_id = ir_model_data._xmlid_lookup('travel_package.package_visa_email_template')[1]
            else:
                template_id = ir_model_data._xmlid_lookup('travel_package.package_visa_email_template_without_welcome_letter')[1]
        except ValueError:
            template_id = False

        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False

        data_ids = []
        if self.visa_return.reservation_type == 'b2c':
            for get in self.get_visa_now_e():
                report_template_id = self.env['ir.actions.report'].sudo()._render_qweb_pdf('welcome_letter_report.welcome_letter_report_id',get.ids)
                data_record = base64.b64encode(report_template_id[0])
                ir_values = {
                'name': "Welcome Letter - {0}.pdf".format(get.visa_return.partner_id.name),
                'type': 'binary',
                'datas': data_record,
                'store_fname': data_record,
                'mimetype': 'application/pdf',
                }
                data_id = self.env['ir.attachment'].create(ir_values)
                data_ids.append(data_id.id)
       
        ctx = {
           'default_model': 'all.services',
           'default_res_ids': self.ids,
           # 'default_use_template': bool(template_id),
           'default_template_id': template_id,
           'default_composition_mode': 'comment',
           'default_email_layout_xmlid': "mail.mail_notification_layout_with_responsible_signature",
           'default_attachment_ids': [(6, 0, data_ids)]
        }

        
        return {
           'name': _('Visa Email'),
           'type': 'ir.actions.act_window',
           'view_mode': 'form',
           'res_model': 'mail.compose.message',
           'views': [(compose_form_id, 'form')],
           'view_id': compose_form_id,
           'target': 'new',
           'context': ctx,
        }

    def get_visa_now_e(self):
        self.ensure_one()
        same_visa = []
        for ho in self.visa_return.visa_pkg:
            if ho.supplier and self.supplier and ho.supplier.id == self.supplier.id:
                same_visa.append(ho.supplier.id)

        if same_visa and self.supplier and self.supplier.id in same_visa:
            return self.env['all.services'].search([
                ('visa_return', '=', self.visa_return.id),
                ('supplier', 'in', same_visa),
            ])
        return self

    def action_hotel_email_historys(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'History',
            'res_model': 'mail.message',
            'view_type': 'form',
            'view_mode': 'list,form',
            'domain': [('res_id', '=',self.id),('model', '=','all.services')],  
        }

    def action_ready_packg_email_sent(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            if self.package_return.reservation_type == 'b2c':
                template_id = ir_model_data._xmlid_lookup('travel_package.package_ready_package_email_template')[1]
            else:
                template_id = ir_model_data._xmlid_lookup('travel_package.package_ready_package_email_template_without_welcome_letter')[1]
        except ValueError:
            template_id = False

        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False

        data_ids = []
        if self.package_return.reservation_type == 'b2c':



            for get in self.get_ready_package_now_e():
                report_template_id = self.env['ir.actions.report'].sudo()._render_qweb_pdf('welcome_letter_report.welcome_letter_report_id',get.ids)
                data_record = base64.b64encode(report_template_id[0])
                ir_values = {
                'name': "Welcome Letter - {0}.pdf".format(get.package_return.partner_id.name),
                'type': 'binary',
                'datas': data_record,
                'store_fname': data_record,
                'mimetype': 'application/pdf',
                }
                data_id = self.env['ir.attachment'].create(ir_values)
                data_ids.append(data_id.id)
       
        ctx = {
           'default_model': 'all.services',
           'default_res_ids': self.ids,
           # 'default_use_template': bool(template_id),
           'default_template_id': template_id,
           'default_composition_mode': 'comment',
           'default_email_layout_xmlid': "mail.mail_notification_layout_with_responsible_signature",
           'default_attachment_ids': [(6, 0, data_ids)]
        }

        
        return {
           'name': _('Ready Package Email'),
           'type': 'ir.actions.act_window',
           'view_mode': 'form',
           'res_model': 'mail.compose.message',
           'views': [(compose_form_id, 'form')],
           'view_id': compose_form_id,
           'target': 'new',
           'context': ctx,
        }
    def get_ready_package_now_e(self):
        self.ensure_one()
        same_ready_package = []
        for ho in self.package_return.packages_pkg:
            if ho.supplier and self.supplier and ho.supplier.id == self.supplier.id:
                same_ready_package.append(ho.supplier.id)

        if same_ready_package and self.supplier and self.supplier.id in same_ready_package:
            return self.env['all.services'].search([
                ('package_return', '=', self.package_return.id),
                ('supplier', 'in', same_ready_package),
            ])
        return self

    def action_other_service_email_sent(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            if self.otherservices_return.reservation_type == 'b2c':
                template_id = ir_model_data._xmlid_lookup('travel_package.other_services_email_template')[1]
            else:
                template_id = ir_model_data._xmlid_lookup('travel_package.other_services_email_template_without_welcome_letter')[1]
        except ValueError:
            template_id = False

        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False

        data_ids = []
        if self.otherservices_return.reservation_type == 'b2c':
            for get in self.get_other_services_e():
                report_template_id = self.env['ir.actions.report'].sudo()._render_qweb_pdf('welcome_letter_report.welcome_letter_report_id',get.ids)
                data_record = base64.b64encode(report_template_id[0])
                ir_values = {
                'name': "Welcome Letter - {0}.pdf".format(get.otherservices_return.partner_id.name),
                'type': 'binary',
                'datas': data_record,
                'store_fname': data_record,
                'mimetype': 'application/pdf',
                }
                data_id = self.env['ir.attachment'].create(ir_values)
                data_ids.append(data_id.id)

        ctx = {
           'default_model': 'all.services',
           'default_res_ids': self.ids,
           # 'default_use_template': bool(template_id),
           'default_template_id': template_id,
           'default_composition_mode': 'comment',
           'default_attachment_ids': [(6, 0, data_ids)]
        }

        
        return {
           'name': _('Other Services Email'),
           'type': 'ir.actions.act_window',
           'view_mode': 'form',
           'res_model': 'mail.compose.message',
           'views': [(compose_form_id, 'form')],
           'view_id': compose_form_id,
           'target': 'new',
           'context': ctx,
        }

    def get_other_services_e(self):
        self.ensure_one()
        same_services = []

        for ho in self.otherservices_return.otherservices_pkg:
            if ho.supplier and self.supplier and ho.supplier.id == self.supplier.id:
                same_services.append(ho.supplier.id)

        if same_services and self.supplier and self.supplier.id in same_services:
            return self.env['all.services'].search([
                ('otherservices_return', '=', self.otherservices_return.id),
                ('supplier', 'in', same_services),
            ])
        return self

    def action_cruises_email_sent(self):
            self.ensure_one()
            ir_model_data = self.env['ir.model.data']
            try:
                if self.cruises_return.reservation_type == 'b2c':
                    template_id = ir_model_data._xmlid_lookup('travel_package.cruises_email_template')[1]
                else:
                    template_id = ir_model_data._xmlid_lookup('travel_package.cruises_email_template_without_welcome_letter')[1]
            except ValueError:
                template_id = False

            try:
                compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[1]
            except ValueError:
                compose_form_id = False

            data_ids = []
            if self.cruises_return.reservation_type == 'b2c':

                for get in self.get_cruises_e():
                    report_template_id = self.env['ir.actions.report'].sudo()._render_qweb_pdf('welcome_letter_report.welcome_letter_report_id',get.ids)
                    data_record = base64.b64encode(report_template_id[0])
                    ir_values = {
                    'name': "Welcome Letter - {0}.pdf".format(get.cruises_return.partner_id.name),
                    'type': 'binary',
                    'datas': data_record,
                    'store_fname': data_record,
                    'mimetype': 'application/pdf',
                    }
                    data_id = self.env['ir.attachment'].create(ir_values)
                    data_ids.append(data_id.id)

            ctx = {
               'default_model': 'all.services',
               'default_res_ids': self.ids,
               'default_use_template': bool(template_id),
               'default_template_id': template_id,
               'default_composition_mode': 'comment',
               'default_attachment_ids': [(6, 0, data_ids)]
            }

            
            return {
               'name': _('Cruises Email'),
               'type': 'ir.actions.act_window',
               'view_mode': 'form',
               'res_model': 'mail.compose.message',
               'views': [(compose_form_id, 'form')],
               'view_id': compose_form_id,
               'target': 'new',
               'context': ctx,
            }


    def get_cruises_e(self):
        self.ensure_one()
        same_cruises = []
        for ho in self.cruises_return.cruises_pkg:
            if ho.supplier and self.supplier and ho.supplier.id == self.supplier.id:
                same_cruises.append(ho.supplier.id)

        if same_cruises and self.supplier and self.supplier.id in same_cruises:
            return self.env['all.services'].search([
                ('cruises_return', '=', self.cruises_return.id),
                ('supplier', 'in', same_cruises),
            ])
        return self

    def action_yachat_email_sent(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            if self.yacht_return.reservation_type == 'b2c':
                template_id = ir_model_data._xmlid_lookup('travel_package.yacht_email_template')[1]
            else:
                template_id = ir_model_data._xmlid_lookup('travel_package.yacht_email_template_without_welcome_letter')[1]
        except ValueError:
            template_id = False

        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        data_ids = []
        if self.yacht_return.reservation_type == 'b2c':
            for get in self.get_yacht_now_e():
                report_template_id = self.env['ir.actions.report'].sudo()._render_qweb_pdf('welcome_letter_report.welcome_letter_report_id',get.ids)
                data_record = base64.b64encode(report_template_id[0])
                ir_values = {
                'name': "Welcome Letter - {0}.pdf".format(get.yacht_return.partner_id.name),
                'type': 'binary',
                'datas': data_record,
                'store_fname': data_record,
                'mimetype': 'application/pdf',
                }
                data_id = self.env['ir.attachment'].create(ir_values)
                data_ids.append(data_id.id)
        ctx = {
           'default_model': 'all.services',
           'default_res_ids': self.ids,
           # 'default_use_template': bool(template_id),
           'default_template_id': template_id,
           'default_composition_mode': 'comment',
           'default_attachment_ids': [(6, 0, data_ids)]
        }

        
        return {
           'name': _('Yacht Email'),
           'type': 'ir.actions.act_window',
           'view_mode': 'form',
           'res_model': 'mail.compose.message',
           'views': [(compose_form_id, 'form')],
           'view_id': compose_form_id,
           'target': 'new',
           'context': ctx,
        }


    def get_yacht_now_e(self):
        self.ensure_one()
        same_yact = []

        for ho in self.yacht_return.yacht_pkg:
            if ho.supplier and self.supplier and ho.supplier.id == self.supplier.id:
                same_yact.append(ho.supplier.id)

        if same_yact and self.supplier and self.supplier.id in same_yact:
            return self.env['all.services'].search([
                ('yacht_return', '=', self.yacht_return.id),
                ('supplier', 'in', same_yact),
            ])
        return self

    def action_private_jet_email_sent(self):
            self.ensure_one()
            ir_model_data = self.env['ir.model.data']
            try:
                if self.privatejet_return.reservation_type == 'b2c':
                    template_id = ir_model_data._xmlid_lookup('travel_package.private_jet_email_template')[1]
                else:
                    template_id = ir_model_data._xmlid_lookup('travel_package.private_jet_email_template_without_welcome_letter')[1]
            except ValueError:
                template_id = False

            try:
                compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[1]
            except ValueError:
                compose_form_id = False
            data_ids = []
            if self.privatejet_return.reservation_type == 'b2c':
                for get in self.get_private_jet_now_e():
                    report_template_id = self.env['ir.actions.report'].sudo()._render_qweb_pdf('welcome_letter_report.welcome_letter_report_id',get.ids)
                    data_record = base64.b64encode(report_template_id[0])
                    ir_values = {
                    'name': "Welcome Letter - {0}.pdf".format(get.privatejet_return.partner_id.name),
                    'type': 'binary',
                    'datas': data_record,
                    'store_fname': data_record,
                    'mimetype': 'application/pdf',
                    }
                    data_id = self.env['ir.attachment'].create(ir_values)
                    data_ids.append(data_id.id)
            ctx = {
               'default_model': 'all.services',
               'default_res_ids': self.ids,
               'default_use_template': bool(template_id),
               'default_template_id': template_id,
               'default_composition_mode': 'comment',
               'default_attachment_ids': [(6, 0, data_ids)]
            }

            
            return {
               'name': _('Private Jet Email'),
               'type': 'ir.actions.act_window',
               'view_mode': 'form',
               'res_model': 'mail.compose.message',
               'views': [(compose_form_id, 'form')],
               'view_id': compose_form_id,
               'target': 'new',
               'context': ctx,
            }


    def get_private_jet_now_e(self):
        self.ensure_one()
        same_private_jet = []
        for ho in self.privatejet_return.privatejet_pkg:
            if ho.supplier and self.supplier and ho.supplier.id == self.supplier.id:
                same_private_jet.append(ho.supplier.id)

        if same_private_jet and self.supplier and self.supplier.id in same_private_jet:
            return self.env['all.services'].search([
                ('privatejet_return', '=', self.privatejet_return.id),
                ('supplier', 'in', same_private_jet),
            ])
        return self

    def get_default_product(self):

        if self.service_type != False:
            search = ('id','!=',False)
            if self.service_type == 'flight':
                search = ('prod_serv_typecategory', '=','flight')
            if self.service_type == 'hotel':
                search = ('prod_serv_typecategory', '=','hotel')
            if self.service_type == 'transfer':
                search = ('prod_serv_typecategory', '=','transfer')
            if self.service_type == 'tours':
                search = ('prod_serv_typecategory', '=','tour')
            if self.service_type == 'visa':
                search = ('prod_serv_typecategory', '=','visa')
            if self.service_type == 'ready_package':
                search = ('prod_serv_typecategory', '=','package')
            if self.service_type == 'private_jet':
                search = ('prod_serv_typecategory', '=','private')
            if self.service_type == 'yacht':
                search = ('prod_serv_typecategory', '=','yacht')
            if self.service_type == 'cruise':
                search = ('prod_serv_typecategory', '=','cruise')
            if self.service_type == 'other':
                search = ('prod_serv_typecategory', '=','other')
            record = self.env['product.product'].search([search],limit=1)
            self.product_id = record.id

class YachtType(models.Model):
    _name = 'yacht.type'
    _description = "Yacht Type"
    _rec_name = 'name'
    name = fields.Char(string='Name')

class ElectronicTicket(models.Model):
    _name = 'electronic.ticket'
    _description = "Electronic Ticket"
    _rec_name = 'name'
    name = fields.Char(string='Name')

class HotelTransfer(models.Model):
    _name = 'hotel.transfer'
    _description = "Hotel Transfer"
    _rec_name = 'name'
    name = fields.Char(string='Name')

    def unlink(self):

        all_services = self.env['all.services'].search([])
        for v in all_services:
            if v.transfer:
                for x in v.transfer:
                    for y in self:
                        if x.name == y.name:
                            raise ValidationError(_("You cannot delete this beacuse the record already exists for this service"))
                        

            
        recs = super(hotel_transfer_ext, self).unlink()
        return recs

class CabinType(models.Model):
    _name = 'cabin.type'
    _description = "Cabin Type"
    _rec_name = 'name'
    name = fields.Char(string='Name')

class CostManage(models.Model):
    _name = 'cost.manage'
    _description ="Cost Manage"
    no_of_pax =fields.Integer(string="Alternatin No of Person")
    no_of_foc=fields.Integer("No Of FOC")
    seat_capacity=fields.Many2one('product.product',string="Seat Capacity", domain="[('custom_value','=',True)]")
    single_supp=fields.Float(string="Single Supp")
    group_cost=fields.Float(string="Group Cost")
    manage_return = fields.Many2one('reservation.order')


class TransferType(models.Model):
    _name = 'transfer.type'
    _description = "Transfer Type"
    _rec_name = 'name'
    name =fields.Char(string="Name")

class VehicleType(models.Model):
    _name = 'vehicle.type'
    _description = "Vehicle Type"
    _rec_name = 'name'
    name =fields.Char(string="Name")

class WaitTimePolicy(models.Model):
    _name = 'wait.time.policy'
    _description ="Wait Time Policy"
    _rec_name = 'name'
    name =fields.Char(string="Alternatin No of Person")

class airline(models.Model):
    _name= 'airline.name'
    _description = "Airline Name"
    _rec_name ='name'
    name = fields.Char(string="Airline")

class source(models.Model):
    _name= 'source.name'
    _description = "Source name"
    _rec_name ='name'
    name = fields.Char(string="Source name")

class destination(models.Model):
    _name= 'destination.name'
    _description = "Destination Name"
    _rec_name ='name'

    display_name = fields.Char(string="Display Name",compute="get_display_name")
    name = fields.Char(string="Destination Name",copy=False)
    country_id = fields.Many2one('res.country', string='Country',copy=False,required=True)

    def get_display_name(self):
        for dest in self:
            dest.display_name = str(dest.name) + ' (' + str(dest.country_id.name) + ')'

class tickettype(models.Model):
    _name= 'ticket.type'
    _description = "Ticket Type"
    _rec_name ='ticket_type'
    ticket_type = fields.Char(string="Ticket Type")

class Meal_Plan(models.Model):
    _name= 'meal.plan'
    _description = "Meal Plan"
    _rec_name ='name'

    name = fields.Char(string="Name")


    def unlink(self):

        all_services = self.env['all.services'].search([])
        for v in all_services:
            if v.meal_plan:
                for x in v.meal_plan:
                    for y in self:
                        if x.name == y.name:
                            raise ValidationError(_("You cannot delete this beacuse the record already exists for this service"))
                        
            
        recs = super(meal_plan_ext, self).unlink()
        return recs
        
class quotation(models.Model):
    _name= 'quot.name'
    _description = "Quot Name"
    _rec_name ='name'
    name = fields.Char(string="Quotation")

class MealClass(models.Model):
    _name= 'meal.class'
    _rec_name ='name'
    _description = "Meal class"

    name = fields.Char(string="Meal")


class daysname(models.Model):
    _name= 'days.name'
    _description = "Days Name"
    _rec_name ='days'
    days = fields.Char(string="Day")


class menutype(models.Model):
    _name= 'menu.type'
    _description = "Menu Type"
    _rec_name ='name'
    name = fields.Char(string="Menu")



class roomoccupancy(models.Model):
    _name= 'room.occupancy'
    _description = "Room Occupancy"
    _rec_name ='name'


    name = fields.Char(string="Name ")
    no_of_person =fields.Char(string="No. of Guests")
    room_selection = fields.Many2one('room.selection',string="Room Selection")

class RoomSelection(models.Model):
    _name= 'room.selection'
    _description = "Room Selection"
    _rec_name ='name'

    name = fields.Char(string="Room Selection")

class roomtype(models.Model):
    _name= 'room.type'
    _description = "Room Type"
    _rec_name ='name'


    name = fields.Char(string="Room Type")

    def unlink(self):

        all_services = self.env['all.services'].search([])
        for v in all_services:
            if v.room_type:
                for x in v.room_type:
                    for y in self:
                        if x.name == y.name:
                            raise ValidationError(_("You cannot delete this beacuse the record already exists for this service"))
                        

            
        recs = super(room_type_ext, self).unlink()
        return recs
class NationalityofClient(models.Model):
    _name= 'nationality.name'
    _description = "National Name"
    name = fields.Char(string="Country")

class CompanyofClient(models.Model):
    _name= 'company.name'
    _description = "Company Name"
    name = fields.Char(string="Company name")

class frequentflier(models.Model):
    _name= 'frequent.flier'
    _description = "Frequent Flyer" 
    _rec_name = 'membership_name'

    membership_name = fields.Char(string="Membership Name")
    membership_id = fields.Char(string="Membership ID")
    contact_link = fields.Many2one('res.partner')

class SubCustomer(models.Model):
    _name = 'sub.customer'
    _description = "Sub Customer"
    customer_name = fields.Many2one('res.partner',"Customer Name",required=True)
    relation = fields.Char("Relation")
    dob = fields.Date('DOB')
    age = fields.Char("Age")
    title = fields.Many2one('res.partner.title', string="Title")
    b2c_customer = fields.Boolean("B2C Customer", related='customer_return.b2c_customer')
    category = fields.Selection([('infant', 'Infant'),
    ('child', 'Child'),
    ('adult', 'Adult')],string='Category')
    passport_no = fields.Char(string='Passport No')
    national_id = fields.Char(string='National Id No')
    nationality_of_client = fields.Many2one('res.country',string="Nationality")
    customer_return = fields.Many2one('res.partner')

    def _get_customer_sync_vals(self):
        self.ensure_one()
        vals = {
            'dob': self.dob,
            'passport_no': self.passport_no,
            'national_id': self.national_id,
            'nationality_of_client': self.nationality_of_client.id,
            'category': self.category,
        }
        if 'title_id' in self.customer_name._fields:
            vals['title_id'] = self.title.id
        elif 'title' in self.customer_name._fields:
            vals['title'] = self.title.id
        return vals

    def _sync_customer_details(self):
        for rec in self:
            if rec.customer_name:
                rec.customer_name.write(rec._get_customer_sync_vals())

    @api.model
    def create(self, vals):
        new_rec = super(SubCustomer, self).create(vals)
        new_rec._sync_customer_details()
        return new_rec


    def write(self, vals):
        rec = super(SubCustomer, self).write(vals)
        self._sync_customer_details()
        return rec

    @api.onchange('customer_name')
    def black_list_warning(self):
        if self.customer_name:
            if self.customer_name.blacklist:
                return {'value':{},'warning':{'title':
                        'warning','message':"This is a blacklist customer."}}

    @api.onchange('dob')
    def _comuteage(self):
        if self.dob:
            year = (date.today() - self.dob) // timedelta(days=365.2425)
            nofmonths=  date.today().month - self.dob.month
            if nofmonths < 0: # if statement in case the current month is less than the birth minth
                nofmonths = 12 + nofmonths
            if nofmonths == 0:
                year += 1
            self.age = str(year)+" Years "+str(nofmonths) +" Months "


    @api.onchange('customer_name')
    def get_detals(self):
        if self.customer_name:
            self.dob = self.customer_name.dob
            self.passport_no =self.customer_name.passport_no
            self.nationality_of_client =self.customer_name.nationality_of_client
            self.national_id =self.customer_name.national_id

class CustomerEvent(models.Model):
    _name = 'customer.event'
    _description ="Customer Event"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    date = fields.Date(string="Date")
    event = fields.Char(string="Occasion Description")
    enable = fields.Boolean(string="Enable")
    event_return = fields.Many2one('res.partner')

    @api.model
    def send_notification(self):
        current_date = fields.Date.today()
        for event_rec in self.env['customer.event'].search([]):
            if (event_rec.date - current_date).days <= 7:
                mail_obj = self.env['mail.mail']
                self.env['mail.activity'].create({
                  'res_id': event_rec.id,
                  'res_model_id': self.env['ir.model']._get('customer.event').id,
                  'activity_type_id': self.env.ref('travel_package.activity_type').id,
                  'summary': "Event " +event_rec.event + " is going to happen.",
                  'note': "Hi. Event " +event_rec.event + " is going to happen of customer "+event_rec.event_return.name,
                  'user_id': event_rec.create_uid.id,
                })

        recs = self.env['account.move'].search([('move_type','=','out_invoice'),('state','=','posted'),('payment_state','not in',['paid'])])
        for x in recs:
            if x.payment_date_custom:
                if (x.payment_date_custom - current_date).days <= 7:
                    channel_id = record_id = self.env.ref('travel_package.customer_notification_channel').id
                    partner_recs = self.env['res.partner'].search([])
                    rec = self.env['mail.message'].create({
                        'model': 'mail.channel',
                        'res_id': channel_id, #from/reference channel
                        'body': x.partner_id.name+" has due amount of "+str(x.amount_residual)+" "+x.currency_id.name+" against Reservation No: "+x.package_no+" due on: "+str(x.payment_date_custom),
                        'channel_ids': [channel_id], #channel ID to post to
                        'author_id': 1,
                        'author_avatar': False
                        })

    def sendEmailonclick(self):
        mail_obj = self.env['mail.mail']
        date_today = date.today()
        date_today = str(date_today)
        records = self.env['customer.event'].search([])
        for x in records:
            if x.date:
                datenow = x.date
                datenow = str(datenow)
                if str(date_today[5:10]) == str(datenow[5:10]):
                    mail_obj.create({
                    'email_to': 'email_to@gmail.com',
                    'subject': "Event Reminder",
                    'body_html':
                    '''<span  style="font-size:14px"><br/>
                        <br/>%s </span>
                        <br/>%s </span> %s </span>
                        <br/>%s </span> %s </span>
                        <br/>%s </span> %s </span> %s</span>
                        <br/>%s</span>
                        <br/>%s</span>
                        <br/>%s</span>
                        <br/><br/>''' % (x.event_return.name,"Event of ",x.event ,"is taking place on ",str(x.date)," ",""," ","  ","", "Enterprise-CUBE.PVT.LTD")}).send(self)

class product_product_customized(models.Model):
    _inherit = 'product.product'

    
    term_and_cond = fields.Html("Term & Conditions")
    guide_supplier = fields.Boolean("Is Guide")
    custom_value = fields.Boolean("Is Custom Value")
    validity = fields.Char(string="Validity (Start/Expire)")
    no_of_nights = fields.Integer(string="No of Nights")
    room_type = fields.Many2many('room.type', 'rpom_type_prod_rel', string="Room Type")
    meal_plan = fields.Many2one('meal.plan', string="Meal Plan")
    transfer_mode = fields.Char(string="Transfer Mode")
    added_values = fields.Char(string="Added Values")
    rate = fields.Float(string="Rate")
    product_type = fields.Char(string="Type")
    type = fields.Selection([
        ('consu', _('Consumable')),
        ('service', _('Service'))], string='Product Type', default='service', required=True,
        help='A stockable product is a product for which you manage stock. The "Inventory" app has to be installed.\n'
             'A consumable product, on the other hand, is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.\n'
             'A digital content is a non-material product you sell online. The files attached to the products are the one that are sold on '
             'the e-commerce such as e-books, music, pictures,... The "Digital Product" module has to be installed.')
    prod_serv_typecategory = fields.Selection([
        ('flight', 'Flight'),
        ('hotel', 'Hotel'),
        ('transfer', 'Transfer'),
        ('tour', 'Tour'),
        ('visa', 'Visa'),
        ('package', 'Package'),
        ('private', 'Private Jet'),
        ('yacht', 'Yacht'),
        ('cruise', 'Cruise'),
        ('other', 'Other Service'),
        ],string='Prouct Service Type')
    @api.onchange('name')
    def get_accounts(self):
        if self.categ_id:
            self.property_account_income_id = self.categ_id.property_account_income_categ_id.id
            self.property_account_expense_id = self.categ_id.property_account_expense_categ_id.id
class CompanyContract(models.Model):
    _name = 'company.contract'
    _description = "Company Name"
    _rec_name = 'contract_title'
    contract_title = fields.Char(string="Contract Ttile")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    attachment = fields.Many2many('ir.attachment', 'attachment_ir_attachments_rel', 'class_id', 'attachment_id', 'Attachments')
    partner_link = fields.Many2one('res.partner')

class CompanyAttachments(models.Model):
    _name = 'company.attachments'
    _description = "Company Attachments"
    _rec_name = 'description'
    description = fields.Char(string="Attachment Description")
    attachment = fields.Many2many('ir.attachment', 'comp_attach_ir_attachments_rel', 'class_id', 'comp_attachment_id', 'Attachments')

    partner_link = fields.Many2one('res.partner')

class CompanyNumbersTree(models.Model):
    _name = 'gds.numbers.tree'
    _description = "GDS Number Tee"
    _rec_name = 'gds_type'
    gds_type = fields.Char(string="Type")
    gds_id = fields.Char(string="GDS ID")
    partner_link = fields.Many2one('res.partner')

class CompanyNumbers(models.Model):
    _name = 'gds.numbers'
    _description = "GDS Number "
    _rec_name = 'name'
    name = fields.Char(string="Name")
    gds_id = fields.Char(string="Number")

class CustSmsTemp(models.Model):
    _name = 'custom.sms.temp'
    _description = 'Custom SMS'
    _rec_name = 'template_name'
    template_name = fields.Char(string="Temlpate Name")
    template_msg = fields.Text(string="Template Message")

class CustomSms(models.Model):
    _name = 'custom.sms'
    _description = "Custom SMS"
    _rec_name = 'send_to'
    send_to = fields.Char(string="Numbers")
    sms_tag_name = fields.Selection([
        ('RAWNAQ', 'RAWNAQ'),
        ('RAWNAQ-AD', 'RAWNAQ-AD'),
        ],string='Message Tag')

    sms_send_type = fields.Selection([
        ('now', 'Now'),
        ('later', 'Later'),
        ],string='When?', default='now')
    sms_send_time = fields.Datetime(string="Select Time", default=fields.Datetime.now)
    res_ids = fields.Many2many('res.partner', string='Active IDs')
    sms_template = fields.Many2one('custom.sms.temp', string='Select Template')
    message = fields.Char(string="Characters Remaining")
    sms_text = fields.Text(string="Message")

    @api.onchange('sms_template')
    def get_template(self):
        if self.sms_template:
            self.sms_text = self.sms_template.template_msg

    

    @api.onchange('res_ids')
    def get_default_numbers(self):
        temp_str = ""
        if not self.send_to:
            if self.res_ids:
                for x in self.res_ids:
                    if x.mobile:
                        temp_str = temp_str+x.mobile+","
            self.send_to = temp_str

