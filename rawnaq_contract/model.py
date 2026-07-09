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

from odoo import models, fields, api
from datetime import date
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError, UserError
import json

class VendorBillFormExt(models.Model):
    _inherit = 'account.move'

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
        ],string='Prouct Service Type',readonly=True)


class ContractForm(models.Model):
    _name = 'contract.form'
    _rec_name = 'name'
    _description = 'contract form'

    name = fields.Char()
    supplier = fields.Many2one('res.partner',string="Supplier")
    contract_type = fields.Many2one('contract.type',string="Contract Type")
    date_start = fields.Date(default=datetime.today())
    date_end = fields.Date()
    note = fields.Text()
    product_detail = fields.One2many('contract.info','form_link')
    state = fields.Selection([
        ('new', 'New'),
        ('running', 'Running'),
        ('renew', 'To Renew'),
        ('expired', 'Expired'),
        ('cancel', 'Cancelled'),
        ],default='new',copy = False)

    def action_set_new(self):
        self.state = 'new'
    
    def action_set_running(self):
        self.state = 'running'
    
    def action_set_renew(self):
        self.state = 'renew'
    
    def action_set_expired(self):
        self.state = 'expired'
    
    def action_set_cancel(self):
        self.state = 'cancel'

class ContractType(models.Model):
    _name = 'contract.info'
    _rec_name = 'product'
    _description = 'Contract Info'

    product = fields.Many2one('product.product',string="Product")
    season = fields.Many2one('season.season',string="Season")
    desc = fields.Char(string="Description")
    form_link = fields.Many2one('contract.form')

class SeasonClass(models.Model):
    _name = 'season.season'
    _rec_name = 'name'
    _description = 'Season'

    name = fields.Char(string="Contract Type")

class ContractType(models.Model):
    _name = 'contract.type'
    _rec_name = 'name'
    _description = 'Contract Type'

    name = fields.Char(string="Contract Type")
