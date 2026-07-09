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
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class account_payment_ext(models.Model):
    _inherit = 'account.payment'

    journal_entry = fields.Many2one('account.move', string ="Bank Charges Entry",copy=False)

    @api.depends('reconciled_invoice_ids')
    def get_package_no(self):

        _logger.info("get_package_no")
        # package_no = self.env['account.move'].search([('type','=',self.communication)])
        for rec in self:
            rec.package_no = ""
            if rec.reconciled_invoice_ids:
                for x in rec.reconciled_invoice_ids:
                    if x.package_no:
                        # if x.partner_id.id == rec.partner_id.id:
                        rec.package_no = x.package_no
                        rec.temp = x.package_no
                    else:
                        rec.package_no = ""
                        rec.temp = ""

    package_no = fields.Char(string ="Package No")
    temp = fields.Char(string ="Package No Temp",compute='get_package_no', store=True)

                

    def bank_charges_entry(self):
        is_mada_hyperpay = False
        if self.is_refunded_payment_entry_hp:
            if self.payment_type == 'outbound':
                if 'hyperpay' in str(self.memo).lower():
                    if 'mada' not in str(self.memo).lower():
                        return
                    else:
                        is_mada_hyperpay = True
        currency = self.company_id.currency_id
        round_amt = currency.round
        if not self.journal_id or not self.journal_id.bank_charge:
            return
        lab = ""
        lab_vat = ""
        line_vals = []
        vat_amt = 0.0
        amt = 0.0
        if self.journal_entry:
            move = self.journal_entry
            if move.state == 'posted':
                move.button_draft()
                move.button_cancel()
        if self.journal_id.bank_charge_amt:
            amt = (self.amount * self.journal_id.bank_charge_amt / 100.0) + (self.journal_id.bank_charge_amt1 or 0.0)
            amt = round_amt(amt)
            lab = f"{self.amount} @ {self.journal_id.bank_charge_amt}-{self.name or ''}"
            if self.journal_id.vat_check and self.journal_id.vat:
                lab_vat = f"{self.amount} @ {self.journal_id.vat.amount}% Vat - {self.name or ''}"
                vat_amt = amt * (self.journal_id.vat.amount / 100.0)
                vat_amt = round_amt(vat_amt)
        line_vals.append((0, 0, {
            'name': lab,
            'account_id': self.journal_id.account_id.id,
            'journal_id': self.journal_id.id,
            'debit': 0 if is_mada_hyperpay else amt ,
            'credit': amt if is_mada_hyperpay else 0 ,
        }))
        if self.journal_id.vat_check and self.journal_id.vat:
            vat_account_id = False
            for x in self.journal_id.vat.refund_repartition_line_ids:
                if x.account_id:
                    vat_account_id = x.account_id.id
                    break
            if vat_account_id and vat_amt:
                line_vals.append((0, 0, {
                    'name': lab_vat,
                    'account_id': vat_account_id,
                    'journal_id': self.journal_id.id,
                    'debit': 0 if is_mada_hyperpay else vat_amt,
                    'credit': vat_amt if is_mada_hyperpay else 0,
                }))
        needed_account = False
        if self.payment_type == 'inbound':
            line = self.journal_id.inbound_payment_method_line_ids.filtered(lambda l: l.payment_account_id)[:1]
            needed_account = line.payment_account_id.id if line else False
        elif self.payment_type == 'outbound':
            line = self.journal_id.outbound_payment_method_line_ids.filtered(lambda l: l.payment_account_id)[:1]
            needed_account = line.payment_account_id.id if line else False
        if not needed_account:
            raise UserError("Payment account not configured on the journal.")
        total_credit = round_amt(amt + vat_amt)
        line_vals.append((0, 0, {
            'name': lab,
            'account_id': needed_account,
            'journal_id': self.journal_id.id,
            'debit': total_credit if is_mada_hyperpay else 0,
            'credit': 0 if is_mada_hyperpay else total_credit,
        }))
        if is_mada_hyperpay:
            vals = {
                'ref': '%s (Refunded)'%str(self.name),
                'journal_id': self.journal_id.id,
                'date': self.date,
                'move_type': 'entry',
                'line_ids': line_vals,
            }
        else:
            vals = {
                'ref': '%s (Bank Charges)'%str(self.name),
                'journal_id': self.journal_id.id,
                'date': self.date,
                'move_type': 'entry',
                'line_ids': line_vals,
            }
        move = self.env['account.move'].create(vals)
        self.journal_entry = move.id
        self.journal_entry.action_post()


    @api.onchange('date')
    def onchange_get_dates_in(self):

        get_current_date = datetime.now().date()
        get_current_date_1 = datetime.now().date() - timedelta(days=1)
        get_current_date_2 = datetime.now().date() - timedelta(days=2)
        get_current_date_3 = datetime.now().date() - timedelta(days=3)
        # year, week_num, day_of_week = get_current_date.isocalendar()


        if not self.env.user.payment_admin:
            if datetime.strptime(str(self.date), DEFAULT_SERVER_DATE_FORMAT).date() <= get_current_date:
                if datetime.strptime(str(self.date), DEFAULT_SERVER_DATE_FORMAT).date() in [get_current_date,get_current_date_1,get_current_date_2,get_current_date_3]:
                    return False
                else:
                    raise Warning('Please select a date equal to current date or less/equal to 3 days before the current date!')
                    return { 'value': { 'date': False } }

            else:
                raise Warning('Please select a date equal to current date or less/equal to 3 days before the current date!')
                return { 'value': { 'date': False } }


class AccountMoveReversalExt(models.TransientModel):
    _inherit = 'account.move.reversal'

    @api.onchange('move_type')
    def get_journal_id(self):

        _logger.info("get_journal_id")
        # rec = super(AccountMoveReversalExt, self)._compute_from_moves()
        self.journal_id = self.move_ids[0].journal_id.id if self.move_ids else False
        # return rec

    def _prepare_default_reversal(self, move):
        return {
            'ref': _('Reversal of: %s, %s') % (move.name, self.reason) if self.reason else _('Reversal of: %s') % (move.name),
            'date': self.date or move.date,
            'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
            'journal_id': self.journal_id and self.journal_id.id or move.journal_id.id,
            'invoice_payment_term_id': None,
            'auto_post': 'no',
            'invoice_user_id': move.invoice_user_id.id,
        }

    def reverse_moves(self, is_modify=False):
        moves = self.env['account.move'].browse(self.env.context['active_ids']) if self.env.context.get('active_model') == 'account.move' else self.move_ids
        for move in moves:
            move.mapped('line_ids').remove_move_reconcile()
        return super().reverse_moves(is_modify)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        move_ids = self.env['account.move'].browse(
            self.env.context.get('active_ids', [])
        ) if self.env.context.get('active_model') == 'account.move' else self.env['account.move']

        if not move_ids:
            return res

        today = fields.Date.context_today(self)

        invoice_dates = move_ids.mapped('invoice_date')
        invoice_dates = [d for d in invoice_dates if d]

        if invoice_dates:
            base_date = max(invoice_dates)
        else:
            move_dates = move_ids.mapped('date')
            move_dates = [d for d in move_dates if d]
            base_date = max(move_dates) if move_dates else today

        res['date'] = base_date if base_date > today else today

        return res