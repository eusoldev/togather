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
from odoo.exceptions import ValidationError, UserError
import odoo.exceptions
import datetime as dt
import logging



class res_partner_customized(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'mail.thread', 'mail.activity.mixin']
    private_jet = fields.Boolean(string="Private Jet")  
    mobile = fields.Char(string="Mobile")
    partner_type = fields.Selection([
    ('customer', 'Customer'),
    ('supplier', 'Supplier'),
    ('others', 'Others'),
    ], string="Partner Type",tracking=True)

    def send_email(self):

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data._xmlid_lookup('travel_package.contacts_email_template')[1]
        except ValueError:
            template_id = False

        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
           'default_model': 'res.partner',
           'default_res_ids': self.ids,
           'default_use_template': bool(template_id),
           'default_template_id': template_id,
           'default_composition_mode': 'comment',
        }
        return {
           'name': _('Email'),
           'type': 'ir.actions.act_window',
           'view_mode': 'form',
           'res_model': 'mail.compose.message',
           'views': [(compose_form_id, 'form')],
           'view_id': compose_form_id,
           'target': 'new',
           'context': ctx,
        }

    def sms_wizard(self):

        return {
            'res_model': 'custom.sms',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'name':'Send SMS',
            'view_type': 'form',
            'target': 'new',
            # 'domain': [('invoice_origin','like',self.name)],
             'context': dict(
                default_send_to=self.mobile,
            ),
            }

    def name_get(self):

        res = []
        for partner in self:
            name = partner._get_name()
            res.append((partner.id, name))
        return res


    def _get_name(self):

        """ Utility method to allow name_get to be overrided without re-browse the partner """

        partner = self


        if partner:
            name = partner.name or ''
                # if partner.company_name or partner.parent_id:
            if partner.parent_id:
                if partner.parent_id.name:
                    name = name +", "+partner.parent_id.name
                
            return name

    def create_travel_package(self):

        return {
        'name': _('Travel Package'),
        'type': 'ir.actions.act_window',
        'res_model': 'reservation.order',
        'view_mode': 'form',
        # 'view_id': self.env.ref('view_order_form_ext').id,
        "views": [(self.env.ref('travel_package.view_reservation_order_form').id, "form")],
        'target': 'new',
        'context': {
            'payment_ids': self.ids,
            'default_partner_id': self.id,
            'default_package': 1,
            }
        }


    ind_street = fields.Char(string='Street',tracking=True)
    ind_street2 = fields.Char(string='Street2')
    ind_city = fields.Char(string='City',tracking=True)
    ind_state_id = fields.Many2one('res.country.state', string='State')
    ind_zip = fields.Char(string='Zip')
    ind_country_id = fields.Many2one('res.country', string='Country')
    job_of_company= fields.Many2one('company.name',string="Employee at Company")

    agent = fields.Boolean("Is Agent")
    resturant = fields.Boolean("Resturant")
    supplier_meal = fields.Boolean("Supplier Meal")
    guide_supplier = fields.Boolean("Supplier Guide")
    visa_supplier = fields.Boolean("Visa Company")
    hotel_supplier = fields.Boolean("Hotels")
    ticketing_supplier =fields.Boolean("Supplier Tickets")
    # age = fields.Char("Age",compute='_comuteage' , store=True)
    age = fields.Char("Age")
    sub_customer = fields.One2many('sub.customer','customer_return')
    customer_events = fields.One2many('customer.event','event_return')
    dob =fields.Date('DOB',tracking=True)
    passport_no = fields.Char('Passport No.',tracking=True)
    dmc = fields.Boolean("DMC",tracking=True)
    travel_agency = fields.Boolean("Sub-Agent")
    commission_amount = fields.Float("Commission",tracking=True)
    b2c_customer = fields.Boolean("B2C Customer",tracking=True)
    hotel_link = fields.Char("Hotel link")
    other_user_detaile = fields.Char("User Detail")
    # title = fields.Char("Title")
    package_supplier = fields.Boolean("Package Supplier",tracking=True)
    transfer_supplier = fields.Boolean("Transfer Company",tracking=True)
    airline_supplier = fields.Boolean("Airline Company",tracking=True)
    cruise_supplier = fields.Boolean("Cruise Supplier",tracking=True)
    bed_bank = fields.Boolean("Wholesaler")
    tours_supplier = fields.Boolean("Tours Company",tracking=True)
    yacht_supplier = fields.Boolean("Yacht Company",tracking=True)
    service_supplier = fields.Boolean("Service Provider",tracking=True)
    is_contract = fields.Boolean("Contracted")
    national_id = fields.Char('National Id No.',tracking=True)
    rawnaq_team =   fields.Boolean("Team")
    vip =   fields.Boolean("VIP")
    blacklist = fields.Boolean("Blacklist")
    blacklist_reason = fields.Text("Blacklist Reason")
    nationality_of_client = fields.Many2one('res.country',"Nationality ")
    # nationality_of_client = fields.Many2one('nationality.name',"Nationality ")
    gender = fields.Selection([('male', 'Male'),
    ('female', 'Female')],string='Gender')
    category = fields.Selection([('infant', 'Infant'),
    ('child', 'Child'),
    ('adult', 'Adult')],string='Category')
    frequent_flier= fields.One2many('frequent.flier','contact_link',string="Frequent Flyer ID")
 
    contracts_tree = fields.One2many('company.contract', 'partner_link')
    attachments_tree = fields.One2many('company.attachments', 'partner_link')
    company_numbers = fields.One2many('gds.numbers.tree', 'partner_link')

    national_id_copy = fields.Many2many('ir.attachment', 'national_id_ir_attachments_rel', 'class_id', 'national_id', 'National ID Copy')
    passport_copy = fields.Many2many('ir.attachment', 'passport_copy_ir_attachments_rel', 'class_id', 'passport_id', 'Passport Copy')
    credit_card = fields.Many2many('ir.attachment', 'credit_card_ir_attachments_rel', 'class_id', 'credit_card_id', 'Credit Card')
    business_card = fields.Many2many('ir.attachment', 'bussiness_card_ir_attachments_rel', 'class_id', 'bussines_card_id', 'Business Card')
    other_attachments = fields.Many2many('ir.attachment', 'others_ir_attachments_rel', 'class_id', 'others_id', 'Other Attachments')



    commercial_reg = fields.Many2many('ir.attachment', 'commercial_reg_ir_attachments_rel', 'class_id', 'commercial_reg_id', 'Commercial Registration')
    vat_cert = fields.Many2many('ir.attachment', 'vat_cert_ir_attachments_rel', 'class_id', 'vat_cert_id', 'VAT Certificate')
    non_disc_agre = fields.Many2many('ir.attachment', 'non_disc_agre_ir_attachments_rel', 'class_id', 'non_disc_agre_id', 'Non-disclosure Agrement')
    municiple_lisc = fields.Many2many('ir.attachment', 'municiple_lisc_ir_attachments_rel', 'class_id', 'municiple_lisc_id', 'Municipality License')
    tourism_lisc = fields.Many2many('ir.attachment', 'tourism_lisc_ir_attachments_rel', 'class_id', 'tourism_lisc_id', 'Tourism License (Local or International)')
    chamber_comm_cert = fields.Many2many('ir.attachment', 'chamber_comm_cert_ir_attachments_rel', 'class_id', 'chamber_comm_cert_id', 'Chamber of Commerce Certificate')
    ministry_lab_lisc = fields.Many2many('ir.attachment', 'ministry_lab_lisc_ir_attachments_rel', 'class_id', 'ministry_lab_lisc_id', 'Ministry of Labor License')
    gosi = fields.Many2many('ir.attachment', 'gosi_ir_attachments_rel', 'class_id', 'gosi_id', 'General Organization Social Insurance (GOSI)')
    wasel = fields.Many2many('ir.attachment', 'wasel_ir_attachments_rel', 'class_id', 'wasel_id', 'National Address (Wasel)')

    end_consumer_type = fields.Selection([
        ('social_media', 'Social Media'),
        ('website', 'Website'),
        ('branch', 'Branch'),
        ('others', 'Others'),
        ], 'Type of End User')
    credit_limit = fields.Float(string='Credit Limit')
    # individual_address = fields.Char(string='Individual Address')



    @api.onchange('contracts_tree')
    def check_contract_tree(self):

        if self.contracts_tree:
            self.is_contract = True
        else:
            self.is_contract = False


    @api.onchange('company_type')
    def set_parent_id_onchange(self):

        if self.company_type == 'company':
            self.parent_id = False
            self.ind_street = False
            self.ind_street2 = False
            self.ind_city = False
            self.ind_zip = False
            self.ind_state_id = False
            self.ind_country_id = False
            self.passport_no = False
            self.national_id = False
            self.dob = False
            self.age = False
            self.function = False
            # self.title = False
            self.category = False
            self.gender = False

        else:
            self.street = False
            self.street2 = False
            self.city = False
            self.zip = False
            self.state_id = False
            self.country_id = False

    def notify_dues(self):

        mail_obj = self.env['mail.mail']
        date_today = date.today()
        date_today = str(date_today)


        credit_limit = 0
        invoiced_amount = 0
        payments = 0
        outstanding_amount = 0
        invoice_recs = self.env['account.move'].search([('partner_id','=',self.id),('move_type', '=', 'out_invoice')])
        payment_recs = self.env['account.move'].search([('partner_id','=',self.id),('move_type', '=', 'out_receipt')])

        credit_limit = self.credit_limit
        for x in invoice_recs:
            invoiced_amount += x.amount_total
            outstanding_amount += x.amount_residual

        for y in payment_recs:
            payments += y.amount_total

        mail_obj.create({
        # 'email_to': 'hamza.azeem52@gmail.com',
        'email_to': self.email,
        'subject': "Dues Update",
        'body_html':
        '''<span  style="font-size:14px"><br/>
            <br/>Dear %s ,</span>
            <br/>Summary of your dues are given below.</span>
            <br/>Invoiced Amount: </span> %s </span>
            <br/>Payments: </span> %s </span>
            <br/>Outstanding Amount: </span> %s </span>
            <br/><br/>''' % (self.name,str(invoiced_amount),str(payments),str(outstanding_amount))}).send(self)
            # <br/>Credit Limit: </span> %s </span>
            # <br/><br/>''' % (self.name,str(credit_limit),str(invoiced_amount),str(payments),str(outstanding_amount))}).send(self)

    def postProcessing(message):
        url = "https://x.odoo.com"
        db = 'zzzzzzzzz'
        username = 'xxxxxxx'
        password = 'yyyyyyy'

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        common.version()

        {
            "server_version": "8.0",
            "server_version_info": [8, 0, 0, "final", 0],
            "server_serie": "8.0",
            "protocol_version": 1,
        }

        uid = common.authenticate(db, username, password, {})


        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        id = models.execute_kw(db, uid, password, 'mail.channel', 'create', [{
            'model': 'mail.channel',
            'res_id': 14, #from/reference channel
            'body': message, # here add the message body
            'channel_ids': [14], #channel ID to post to
            'author_id': 1,
            'author_avatar': False
        }])


    def create_contract(self):

        if self.is_contract:
            contracts_rec = self.env['contract.form'].search([('supplier','=',self.id)])
            if not contracts_rec:
                self.env['contract.form'].create({
                    'supplier':self.id,
                    })

    @api.model
    def create(self, vals):
        new_rec = super(res_partner_customized, self).create(vals)
        new_rec.create_contract()
        return new_rec

    def write(self, vals):
        for x in self:
            before=x.write_date
            rec = super(res_partner_customized, x).write(vals)
            for partner in self:
                if 'financial_term' in vals:
                    moves = self.env['account.move'].search([('partner_id','=',partner.id)],limit=1)
                    for move in moves:
                        move.financial_term = vals['financial_term']
            if 'ind_street' in vals or  'ind_street2' in vals or 'ind_state_id' in vals or 'ind_zip' in vals or 'ind_country_id' in vals or 'street' in vals or 'street2' in vals or 'city' in vals or 'state_id' in vals or 'zip' in vals or 'country_id' in vals:
                after = x.write_date
                if before != after:
                    so_recs = x.env['reservation.order'].search([('partner_id','=',x.id),('stages','in',['draft','validate'])])
                    if so_recs:
                        for y in so_recs:
                            if x.company_type == 'person':
                                y.invoice_add = "%s %s %s %s %s %s" %(x.ind_street or '', x.ind_street2 or '', x.ind_city or '', x.ind_state_id.name or '',x.ind_zip or '',x.ind_country_id.name or '')
                                y.delivery_add = "%s %s %s %s %s %s" %(x.ind_street or '', x.ind_street2 or '', x.ind_city or '', x.ind_state_id.name or '',x.ind_zip or '',x.ind_country_id.name or '')
                            if x.company_type == 'company':
                                y.invoice_add = "%s %s %s %s %s %s" %(x.street or '', x.street2 or '', x.city or '', x.state_id.name or '',x.zip or '',x.country_id.name or '')
                                y.delivery_add = "%s %s %s %s %s %s" %(x.street or '', x.street2 or '', x.city or '', x.state_id.name or '',x.zip or '',x.country_id.name or '')
                    x.create_contract()
            return rec

    @api.onchange('dob')
    def _comuteage(self):

        if self.dob:
            if self.dob > fields.Date.today():
                raise ValidationError("DOB can't be greater than current date.")
            else:
                b_day = self.dob
                today_date = date.today()
                years = today_date.year - b_day.year # caculates difference in years
                month = today_date.month - b_day.month# calculates the difference of months
                day = today_date.day - b_day.day # calculates the difference of days
                # if month > 0: # if statement in case the current month is less than the birth minth
                #   month = 12 - month

                if month < 0:
                    years -= 1
                    month = 12 + month
                if day < 0: # if statement in case the current mont is less than the birth month however it will be inaccurate if the birth month is in february
                    day = 31 + day

                self.age = str(years)+" Years "+str(abs(month)) +" Months "
            if years > 12:
                self.category = 'adult'
            elif years <=12 and years >= 2:
                self.category = 'child'
            else:
                self.category = 'infant'

class ResPartnerBankExt(models.Model):
    _inherit = 'res.partner.bank'

    account_name = fields.Char(string='Account Name')
    iban = fields.Char(string='IBAN')
    swift_code = fields.Char(string='Swift Code')
    bank_address = fields.Char(string='Bank Address')
    currency = fields.Char(string='Bank Currency')
    phone_no = fields.Char(string='Phone No')
    email = fields.Char(string='Email')

class res_partner_title(models.Model):
    _name = 'res.partner.title'
    _description = 'Partner Title'
    _order = 'sequence_title, name'

    name = fields.Char(string='Title', required=True, translate=True)
    shortcut = fields.Char(string='Abbreviation', translate=True)
    sequence_title = fields.Integer(string="Sequence")
    active = fields.Boolean(string="Active", default=True)

class ResBankFormExt(models.Model):
    _inherit = 'res.bank'

    iban = fields.Char("IBAN")
    swift_code = fields.Char("Swift Code")
    logo = fields.Binary("Logo")
    add = fields.Boolean("Add Invoice")

class res_company_customized(models.Model):
    _inherit = 'res.company'

    foot = fields.Char()
    foot = fields.Binary(string='Quot Footer')
    foot_tour = fields.Binary(string='Quot inst')
    foot_con = fields.Binary(string='Quot concierge')
    foot_mal = fields.Binary(string='Quot Mal')
    foot_snap = fields.Binary(string='Snap Mal')
    custom_thank_you= fields.Text("Send Thank You Message")
    header_image =fields.Binary(string="itinerary header")

class UsersEXT(models.Model):
    _inherit = 'res.users'

    payment_admin = fields.Boolean(string='Payment admin',help="This Check Box is for payment date purpose")