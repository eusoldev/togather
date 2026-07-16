# -*- coding: utf-8 -*-

from datetime import datetime, date

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError, UserError


class ContractCurrency(models.Model):
    _name = 'contract.currency'
    _rec_name = 'name'
    _description = "Contract Currency"
    name = fields.Char('Currency Name')


class ContractnOffer(models.Model):
    _name = 'contract.offer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'hotel_name'
    _description = "Contract Offer"

    country_name = fields.Many2one('res.country', string="Country Name", tracking=True)
    contract_currency = fields.Many2one('contract.currency', string="Currency", tracking=True)
    hotel_name  = fields.Many2one('hotel.form', string="Hotel Name", tracking=True)
    date = fields.Date(string="Date", tracking=True)
    hotel_type  = fields.Selection([
        ('ultra', 'Ultra Luxury'),
        ('luxury', 'Luxury'),
        ('premium', 'Premium'),
        ('deluxe', 'Deluxe'),
        ('standard', 'Standard'),
        ('other_destinations', 'Other Destinations'),
        ], string="Type")
    add_new_hotel_types = fields.Many2one('new.hotel.add_types'  , required=False , string="Type")
    tree_link_id = fields.One2many('contract.offer.tree', 'tree_link', tracking=True)
    tree_link_id_2 = fields.One2many('contract.tree', 'tree_link_2', tracking=True)
    tree_link_id_3 = fields.One2many('contract.tree.offer', 'tree_link_3', tracking=True)
    tree_link_id_4 = fields.One2many('contract.tree.others', 'tree_link_4', tracking=True)
    tree_link_id_5 = fields.One2many('contract.tree.others', 'tree_link_5', tracking=True)

    @api.model
    def _contract_booking_expiry(self):
        current_date = date.today()
        contract_recs = self.env['contract.offer'].search([])
        for index in contract_recs:
            for package in index.tree_link_id_2:
                package.set_expiry_state(current_date)
            for package in index.tree_link_id_3:
                package.set_expiry_state(current_date)
            for package in index.tree_link_id_4:
                package.set_expiry_state(current_date)


class ContractOfferTree(models.Model):
    _name = 'contract.offer.tree'
    _rec_name = 'Validity_from'
    _description = 'contract Offer tree'

    # contract = fields.Binary(string="Contract")
    contract = fields.Binary(string="Contract", attachment=True)
    # url = fields.Char("URL", compute="_get_url")
    new_url = fields.Char("URL")
    Validity_from = fields.Char(string="Name/Year")
    upload_date = fields.Date(string="Uploaded Date")
    status = fields.Selection([
        ('valid', 'Valid'),
        ('not_valid', 'Not Valid')
    ], string="Status")
    note = fields.Char(string="Note")
    tree_link = fields.Many2one('contract.offer')

    # @api.depends('contract')
    def _get_url(self):
        _logger.info ("11111")
        for rec in self:
            if rec.contract:
                if isinstance(rec.id, int):

                    self.env.cr.execute(" SELECT url FROM ir_attachment WHERE res_model = 'contract.offer.tree' AND res_id =" +str(rec.id))
                    my_url = self.env.cr.fetchall()

                    if my_url:
                        # rec.url = my_url[0][0]
                        rec.new_url = my_url[0][0]

    def write(self, vals):
        if 'contract' in vals and vals['contract']:
            vals['upload_date'] =datetime.today()
            for rec in self:
                if isinstance(rec.id, int):

                    self.env.cr.execute(" SELECT url FROM ir_attachment WHERE res_model = 'contract.offer.tree' AND res_id =" +str(rec.id))

                    my_url = self.env.cr.fetchall()

                    if my_url:
                        # rec.url = my_url[0][0]
                        _logger.info ("1111111111111111111111111111")
                        _logger.info (my_url[0][0])
                        vals['new_url'] = my_url[0][0]

        return super(ContractOfferTree, self).write(vals)
        # return res

    def unlink(self):
        for rec in self:
            self.env.cr.execute("DELETE FROM ir_attachment WHERE id =" +str(rec.id))
            self.env.cr.execute("DELETE FROM ir_attachment WHERE res_id =" +str(rec.id))
        return super(ContractOfferTree, self).unlink()


    @api.model
    def create(self, vals):
        new_rec = super(ContractOfferTree, self).create(vals)
        if new_rec.contract:
            new_rec.upload_date =datetime.today()
            new_rec._get_url()
        return new_rec

class ContractTree(models.Model):
    _name = 'contract.tree'
    _rec_name = 'Validity_from'
    _description = 'contract Tree'


    # contract = fields.Binary(string="Package")
    contract = fields.Binary(string="Package", attachment=True)
    # url = fields.Char("URL", compute="_get_url")
    new_url = fields.Char("URL")
    Validity_from = fields.Char(string="Name/Year")
    upload_date = fields.Date(string="Uploaded Date")
    book_by_date = fields.Date(string="Book By Date")
    status = fields.Selection([
        ('valid', 'Valid'),
        ('not_valid', 'Not Valid')
    ], string="Status")
    note = fields.Char(string="Note")
    tree_link_2 = fields.Many2one('contract.offer')

    def unlink(self):
        for rec in self:
            self.env.cr.execute("DELETE FROM ir_attachment WHERE id =" +str(rec.id))
            self.env.cr.execute("DELETE FROM ir_attachment WHERE res_id =" +str(rec.id))
        return super(ContractTree, self).unlink()

    # @api.depends('contract')
    def _get_url(self):
        _logger.info ("11111")
        for rec in self:
            # rec.url = ""
            if rec.contract:
                if isinstance(rec.id, int):

                    self.env.cr.execute(" SELECT url FROM ir_attachment WHERE res_model = 'contract.tree' AND res_id =" +str(rec.id))

                    my_url = self.env.cr.fetchall()

                    if my_url:
                        # rec.url = my_url[0][0]
                        rec.new_url = my_url[0][0]

    def write(self, vals):
        if 'contract' in vals and vals['contract']:
            vals['upload_date'] =datetime.today()
            for rec in self:
                if isinstance(rec.id, int):

                    self.env.cr.execute(" SELECT url FROM ir_attachment WHERE res_model = 'contract.tree' AND res_id =" +str(rec.id))

                    my_url = self.env.cr.fetchall()

                    if my_url:
                        # rec.url = my_url[0][0]
                        _logger.info ("1111111111111111111111111111")
                        _logger.info (my_url[0][0])
                        vals['new_url'] = my_url[0][0]

        return super(ContractTree, self).write(vals)
        # return res

    def set_expiry_state(self, current_date):

        if self.book_by_date:
            if current_date > self.book_by_date:
                self.write({
                    'status':'not_valid',
                    })

    @api.model
    def create(self, vals):
        new_rec = super(ContractTree, self).create(vals)
        if new_rec.contract:
            new_rec.upload_date =datetime.today()
            new_rec._get_url()
        return new_rec


class ContractTreeOffer(models.Model):
    _name = 'contract.tree.offer'
    _description = 'contract Offer tree'
    _rec_name = 'Validity_from'

    # contract = fields.Binary(string="Offer")
    contract = fields.Binary(string="Offer", attachment=True)
    new_url = fields.Char("URL")
    Validity_from = fields.Char(string="Name/Year")
    upload_date = fields.Date(string="Uploaded Date")
    book_by_date = fields.Date(string="Book By Date")
    status = fields.Selection([
        ('valid', 'Valid'),
        ('not_valid', 'Not Valid')
    ], string="Status")
    note = fields.Char(string="Note")
    tree_link_3 = fields.Many2one('contract.offer')

    def unlink(self):
        for rec in self:
            self.env.cr.execute("DELETE FROM ir_attachment WHERE id =" +str(rec.id))
            self.env.cr.execute("DELETE FROM ir_attachment WHERE res_id =" +str(rec.id))
        return super(ContractTreeOffer, self).unlink()

    # @api.depends('contract')
    def _get_url(self):
        _logger.info ("11111")
        for rec in self:
            # rec.url = ""
            if rec.contract:
                if isinstance(rec.id, int):

                    self.env.cr.execute(" SELECT url FROM ir_attachment WHERE res_model = 'contract.tree.offer' AND res_id =" +str(rec.id))

                    my_url = self.env.cr.fetchall()

                    if my_url:
                        # rec.url = my_url[0][0]
                        rec.new_url = my_url[0][0]

    def write(self, vals):
        if 'contract' in vals and vals['contract']:
            vals['upload_date'] =datetime.today()
            for rec in self:
                if isinstance(rec.id, int):

                    self.env.cr.execute(" SELECT url FROM ir_attachment WHERE res_model = 'contract.tree.offer' AND res_id =" +str(rec.id))

                    my_url = self.env.cr.fetchall()

                    if my_url:
                        # rec.url = my_url[0][0]
                        _logger.info ("1111111111111111111111111111")
                        _logger.info (my_url[0][0])
                        vals['new_url'] = my_url[0][0]

        return super(ContractTreeOffer, self).write(vals)
        # return res


    def set_expiry_state(self, current_date):
        if self.book_by_date:
            if current_date > self.book_by_date:
                self.write({
                    'status':'not_valid',
                    })

    @api.model
    def create(self, vals):
        new_rec = super(ContractTreeOffer, self).create(vals)
        if new_rec.contract:
            new_rec.upload_date =datetime.today()
            new_rec._get_url()
        return new_rec


class ContractTreeOthers(models.Model):
    _name = 'contract.tree.others'
    _rec_name = 'Validity_from'
    _description = 'contract Offer Other'


    # contract = fields.Binary(string="Offer")
    contract = fields.Binary(string="Others", attachment=True)
    new_url = fields.Char("URL")
    Validity_from = fields.Char(string="Name/Year")
    upload_date = fields.Date(string="Uploaded Date")
    book_by_date = fields.Date(string="Book By Date")
    status = fields.Selection([
        ('valid', 'Valid'),
        ('not_valid', 'Not Valid')
    ], string="Status")
    note = fields.Char(string="Note")
    tree_link_4 = fields.Many2one('contract.offer')
    tree_link_5 = fields.Many2one('contract.offer')


    def unlink(self):
        for rec in self:
            self.env.cr.execute("DELETE FROM ir_attachment WHERE id =" +str(rec.id))
            self.env.cr.execute("DELETE FROM ir_attachment WHERE res_id =" +str(rec.id))
        return super(ContractTreeOthers, self).unlink()

    # @api.depends('contract')
    def _get_url(self):
        _logger.info ("11111")
        for rec in self:
            # rec.url = ""
            if rec.contract:
                if isinstance(rec.id, int):

                    self.env.cr.execute(" SELECT url FROM ir_attachment WHERE res_model = 'contract.tree.others' AND res_id =" +str(rec.id))

                    my_url = self.env.cr.fetchall()

                    if my_url:
                        rec.new_url = my_url[0][0]

    def write(self, vals):
        if 'contract' in vals and vals['contract']:
            vals['upload_date'] =datetime.today()
            for rec in self:
                if isinstance(rec.id, int):

                    self.env.cr.execute(" SELECT url FROM ir_attachment WHERE res_model = 'contract.tree.others' AND res_id =" +str(rec.id))

                    my_url = self.env.cr.fetchall()

                    if my_url:
                        # rec.url = my_url[0][0]
                        _logger.info ("1111111111111111111111111111")
                        _logger.info (my_url[0][0])
                        vals['new_url'] = my_url[0][0]

        return super(ContractTreeOthers, self).write(vals)
        # return res


    def set_expiry_state(self, current_date):
        if self.book_by_date:
            if current_date > self.book_by_date:
                self.write({
                    'status':'not_valid',
                    })
    @api.model
    def create(self, vals):
        new_rec = super(ContractTreeOthers, self).create(vals)
        if new_rec.contract:
            new_rec.upload_date =datetime.today()
            new_rec._get_url()
        return new_rec

    # def write(self, vals):
    #   if 'contract' in vals and vals['contract']:
    #       vals['upload_date'] =datetime.today()
    #   rec = super(ContractTreeOthers, self).write(vals)
    #   return rec

class Hotel_NameForm(models.Model):
    _name = 'hotel.form'
    _description = 'Hotel Form'
    _rec_name = 'name'
    _order = 'name'
    name = fields.Char(string="Name")

class newHotelAddTypes(models.Model):
    _name = "new.hotel.add_types"

    _rec_name = "add_new_hotel_type_name"
    _description = 'Add New Hotel Types'


    add_new_hotel_type_name= fields.Char(string="Hotel Type Name", required=True)
    def unlink(self):

        all_contract = self.env['contract.offer'].search([])

        for v in all_contract:
            if v.add_new_hotel_types.add_new_hotel_type_name == self.add_new_hotel_type_name :
                # print('Passs')
                raise ValidationError(_("You Cannot Delete This Hotel Type ( %s ) Because Data Related To It Is Already Present In Contract & Offer! " % v.add_new_hotel_types.add_new_hotel_type_name))

            
        recs = super(newHotelAddTypes, self).unlink()
        return recs

