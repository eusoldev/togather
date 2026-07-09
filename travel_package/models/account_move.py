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
from contextlib import contextmanager
from odoo.tools.misc import format_amount
import odoo.exceptions
import datetime as dt
import logging
from hijri_converter import convert

class account_account_ext(models.Model):
    _inherit = 'account.account'

    sale =fields.Boolean(string ="Sale")
    purchase =fields.Boolean(string ="Purchase")

class account_move_extend(models.Model):
    _inherit = 'account.move'

    hotel_ids = fields.Many2many('res.partner','hotel_invoice_rel', string='Hotels', compute='_get_hotels')
    customer_id = fields.Many2one('res.partner', "Customer Name", compute = '_get_customer_id', store=True)
    amnt_fc = fields.Float("Amount FC", compute = '_calculate_amnt_fc',store=True)
    payment_term = fields.Char(string ="Payment Term")
    stamp = fields.Boolean("Stamp")
    is_commissioned = fields.Boolean('Is Commissioned', default=False)
    payment_date_custom = fields.Date(string ="Due Payment Date")
    package_no = fields.Char(string ="Package No")
    foreign_currency = fields.Char(string ="Foreign Currency")
    add_bank = fields.Boolean(string ="Add Bank")
    partner_address = fields.Char(string ="Address", compute="_compute_contact_address")
    journal_entry = fields.Many2one('account.move', string ="Bank Entry")
    bank_list = fields.Many2many('account.journal', string ="Bank List")
    lang = fields.Selection(string='Report Language', selection='_get_lang',default='en_US')
    arrival_date = fields.Date("Arrival Date")
    departure_date = fields.Date("Departure Date")
    commissioned = fields.Boolean('Commissioned')
    customer_id = fields.Many2one('res.partner', "Customer")
    financial_term = fields.Selection([
    ('pre_paid', 'Pre-Paid'),
    ('credit', 'Credit'),
    ], string="Financial Term")
    partner_type = fields.Selection([
    ('customer', 'Customer'),
    ('supplier', 'Supplier'),
    ('others', 'Others'),
    ], string="Partner Type",related="partner_id.partner_type")
    type_of_invoice = fields.Selection([
        ('international','International Invoice'),
        ('local','Local Invoice'),
        ],default='local',tracking=True)
    gregorian_date = fields.Date(string='Gregorian Date')
    hijri_date = fields.Char(string='Hijri Date', compute='_compute_hijri_date', store=True)

    def action_open_reservation(self):
        reservation_order = self.env['reservation.order'].search([('name', '=', self.package_no)], limit=1)
        view = self.env.ref("travel_package.view_order_form_ext")
        if reservation_order:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Reservation',
                'res_model': 'reservation.order',
                'view_mode': 'form',
                'res_id': reservation_order.id,
                'target': 'current',
                "views": [(view.id, "form")],
                "view_id": view.id,
            }
        else:
            return {
                'type': 'ir.actions.act_window_close',
            }

    @api.depends('create_date')
    def _compute_hijri_date(self):
        for record in self:
            if record.create_date:
                # Convert Gregorian date to Hijri date
                hijri_date_obj = convert.Gregorian(record.create_date.year, record.create_date.month, record.create_date.day).to_hijri()
                # Add 5 hours to the time component
                new_hour = (record.create_date + timedelta(hours=5)).hour
                # Format the Hijri date
                hijri_date_str = f"{hijri_date_obj.year}-{hijri_date_obj.month}-{hijri_date_obj.day}"
                # Append the updated time
                time_str = f"{new_hour:02d}:{record.create_date.minute:02d}:{record.create_date.second:02d}"
                record.hijri_date = f"{hijri_date_str} {time_str}"
                
    def _get_invoice_proforma_pdf_report_filename(self):
        self.ensure_one()
        return f"{self._get_move_display_name().replace(' ', '_').replace('/', '_')}.pdf"

    def set_financial_term(self):
        for move in self.search([]):
            if move.partner_id:
                move.financial_term = move.partner_id.financial_term
    @api.depends('package_no')
    def _get_customer_id(self):
        for rec in self:
            if rec.move_type == 'in_invoice':
                pkg_rec = self.env['reservation.order'].search([('name', '=', rec.package_no)], limit=1)
                rec.customer_id = pkg_rec.partner_id if pkg_rec else False
            else:
                rec.customer_id = False
    @api.depends('invoice_line_ids')
    def _calculate_amnt_fc(self):
        for rec in self:
            total = 0
            for line in rec.invoice_line_ids:
                total += line.amnt_fc

            rec.amnt_fc = total
    @api.depends('package_no')
    def _get_hotels(self):
        for rec in self:
            hotels = set()  # Using a set to avoid duplicate IDs
            if rec.move_type in ['out_invoice', 'out_refund']:
                sale_pkg_rec = self.env['reservation.order'].search([('name', '=', rec.package_no)])
                if sale_pkg_rec and sale_pkg_rec.hotel_pkg:
                    for hotel in sale_pkg_rec.hotel_pkg:
                        hotels.add(hotel.hotel_id.id)
            if rec.move_type in ['in_invoice', 'in_refund']:
                all_services_recs = self.env['all.services'].search([('bill_id', '!=', False)])

                if all_services_recs:
                    for service in all_services_recs:
                        if service.hotel_id and service.bill_id.id == rec.id:
                            hotels.add(service.hotel_id.id)

            rec.hotel_ids = [(6, 0, list(hotels))]  # Convert set to list before assigning

    @api.onchange('partner_id')
    def get_financial_term_value(self):
        self.financial_term = self.partner_id.financial_term or False


    def action_post(self):
        res = super(account_move_extend,self).action_post()
        for x in self:
            if not x.payment_date_custom and x.move_type in ['in_invoice','out_invoice']:
                raise ValidationError("Please fill Due Payment Date first!")
        return res


    def set_je_date(self):
        moves = self.env['account.move'].search([])
        for x in moves:

            if x.invoice_date:
                sql = "UPDATE account_move SET date = '%s' WHERE id = '%s'" % (x.invoice_date, x.id)
                self._cr.execute(sql)
                sql = "UPDATE account_move_line SET date = '%s' WHERE move_id = '%s'" % (x.invoice_date, x.id)
                self._cr.execute(sql)
                self._cr.commit()

    def invoices(self):
        if self.move_type == 'out_invoice':
            typee = ('move_type','=','in_invoice')
            name = 'Bill'
        if self.move_type == 'in_invoice':
            typee = ('move_type','=','out_invoice')
            name = 'Invoice'

        rec = self.env['account.move'].search([('state','!=','cancel'),('package_no','=',self.package_no),typee])

        return {
           'name': name,
           'type': 'ir.actions.act_window',
           'view_mode': 'list,form',
           'res_model': 'account.move',
           'target': 'current',
           'domain': [('state','!=','cancel'),('package_no','=',self.package_no),typee],
        }


    @api.model
    def _get_lang(self):
        return self.env['res.lang'].get_installed()

    def write(self, vals):
        if 'partner_id' in vals and 'financial_term' not in vals:
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            vals['financial_term'] = partner.financial_term if partner else False

        res = super(account_move_extend, self).write(vals)

        for x in self:
            if x.package_no:
                poackage_records = self.env['reservation.order'].search([('name','=',x.package_no)])
                poackage_records.get_cust_invoice_status_new()
        return res

    @api.model
    def create(self, vals):
        if 'partner_id' in vals and 'financial_term' not in vals:
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            vals['financial_term'] = partner.financial_term if partner else False

        new_rec = super(account_move_extend, self).create(vals)
        new_rec.get_bank_list()
        new_rec.invoice_date_due= new_rec.payment_date_custom 
        return new_rec

    def get_bank_list(self):
        bank = self.env['account.journal'].search([('bank_id.add','=',True)])
        if bank:
            bank_list = []
            for x in bank:
                bank_list.append(x.id)
            self.bank_list = [(6,0,bank_list)]

    @api.onchange('lang')
    def set_partner_language(self):

        if self.partner_id:
            self.partner_id.lang = self.lang

   

    @api.depends('partner_id')
    def _compute_contact_address(self):
        for move in self:
            move.partner_address = move.partner_id._display_address() if move.partner_id else False

    def action_invoice_register_payment(self):

        rec = super(account_move_extend, self).action_invoice_register_payment()
        if self.journal_id:
            if self.journal_id.bank_charge:
                self.create_journal_entry(self.journal_id,self.date)
                if self.journal_id.bank_charge_amt:
                    amt = self.amount_total*self.journal_id.bank_charge_amt/100  
                create_debit = self.create_entry_lines(self.journal_id.default_debit_account_id.id,amt,0,self.journal_entry.id,self.partner_id.name)
                create_credit = self.create_entry_lines(self.journal_id.account_id.id,0,amt,self.journal_entry.id,self.partner_id.name)

        return rec

    

    def button_draft(self):
        rec = super(account_move_extend, self).button_draft()
        if self.journal_entry:
            for x in self.journal_entry.line_ids:
                x.unlink()

        return rec

    def create_journal_entry(self,journal,date):
        if not self.journal_entry:
            create_journal_entry = self.env['account.move'].create({
                'ref': self.name,
                'journal_id': journal.id,
                'date': date,
                'move_type': 'entry',
                })
            self.journal_entry = create_journal_entry.id

    def create_entry_lines(self,account,debit,credit,entry_id,label):
        self.env['account.move.line'].create({
            'account_id':account,
            'partner_id': self.partner_id.id,
            'name': label,
            'debit':debit,
            'credit':credit,
            'move_id':entry_id,
            })

    @contextmanager
    def _check_balanced(self, container):
        ''' Assert the move is fully balanced debit = credit.
        An error is raised if it's not the case.
        '''
        with self._disable_recursion(container, 'check_move_validity', default=True, target=False) as disabled:
            yield
            if disabled:
                return

        unbalanced_moves = self._get_unbalanced_moves(container)
        if unbalanced_moves:
            error_msg = _("An error has occurred.")
            for move_id, sum_debit, sum_credit in unbalanced_moves:
                move = self.browse(move_id)
                error_msg += _(
                    "\n\n"
                    "The move (%(move)s) is not balanced.\n"
                    "The total of debits equals %(debit_total)s and the total of credits equals %(credit_total)s.\n"
                    "You might want to specify a default account on journal \"%(journal)s\" to automatically balance each move.",
                    move=move.display_name,
                    debit_total=format_amount(self.env, sum_debit, move.company_id.currency_id),
                    credit_total=format_amount(self.env, sum_credit, move.company_id.currency_id),
                    journal=move.journal_id.name)
            raise UserError(error_msg)

class AccountMoveLineExt(models.Model):
    _inherit ='account.move.line'
    amnt_fc= fields.Float(string="Net Amount FC")
    dummy_compute= fields.Float(string="Dummy", compute="_compute_amnt_fc")
    currency_fc= fields.Many2one('res.currency', string="Currency FC")
    commission = fields.Float(string="Commission")
    price_unit_ecube = fields.Float(string="Price")
    date_from = fields.Date("Check In")
    date_to = fields.Date("Check Out")
    airline = fields.Many2one('res.partner',"Airline",domain="[('airline_supplier','=',True)]")
    e_ticket = fields.Char(string='E-Ticket')
    airline_pnr = fields.Char(string='Airline PNR')
    e_ticket_m2m = fields.Many2many('electronic.ticket', 'account_move_line_pg_rel',string='E-Ticket')
    room_type = fields.Many2many('room.type', 'room_type_acc_rel', string="Room Type")

    package_line = fields.Many2one('all.services', 'Package Line')

    def set_amnt_fc(self):
        for line in self.search([]):
            line._compute_amnt_fc()

    @api.depends('package_line')
    def _compute_amnt_fc(self):
        for line in self:
            line.dummy_compute = 0.0
            line.amnt_fc = line.package_line.amnt_fc

class account_journal_ext(models.Model):
    _inherit = 'account.journal'

    bank_charge = fields.Boolean('Bank Charges')
    bank_charge_amt = fields.Float('Amount in %')
    bank_charge_amt1 = fields.Float('Charge Amount')
    vat_check = fields.Boolean('Vat Charges')
    vat = fields.Many2one('account.tax','Vat')
    account_id = fields.Many2one('account.account','Bank Charges Account', required=True)

class Accounttaxes_ext(models.Model):
    _inherit = 'account.tax'

    service_tax_type = fields.Selection([
        ('international','International'),
        ('domestic','Domestic'),
        ],tracking=True, string="Service Tax Type")
