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


class OffersBuilderForm(models.Model):
    _name = 'offers.builder'
    _description = 'Offers Builder'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'hotel'


    hotel = fields.Many2one('res.partner',string='Hotel',tracking=True)
    subject = fields.Char(string='Subject')
    offer = fields.Date(string='Offer Validity From',tracking=True)
    offer_to = fields.Date(string='Offer Validity To',tracking=True)
    logo = fields.Binary(string='Logo')
    date_of_stay = fields.Date(string='Date From',tracking=True)
    date_to = fields.Date(string='Date To',tracking=True)
    offers_builder_tree = fields.One2many('offers.builder.tree','tree_link')
    supplement_type_tree = fields.One2many('supplement.type.tree','tree_link')
    package_inclusions = fields.Html(string='Package Inclusions')
    exclusive_benefits = fields.Html(string='Exclusive Benefits')
    honeymooners_benefits = fields.Html(string='Honeymooners Benefits')
    terms_conditions = fields.Html(string='Terms & Conditions')

class OffersBuilderTree(models.Model):
    _name = 'offers.builder.tree'
    _description = 'Offers Builder Tree'
    _rec_name = 'room_type'

    room_type = fields.Many2one('room.type',string='Room Type')
    night_3 = fields.Float(string='3 Nights')
    night_4 = fields.Float(string='4 Nights')
    night_5 = fields.Float(string='5 Nights')
    extra_adult = fields.Float(string='Extra Night')
    supplement_type = fields.Many2one('supplement.type',string='Supplement Type')
    price = fields.Float(string='Price')
    tree_link = fields.Many2one('offers.builder')

class SupplementTypeTree(models.Model):
    _name = 'supplement.type.tree'
    _description = 'Supplement Type Tree'
    _rec_name = 'supplement_type'

    supplement_type = fields.Many2one('supplement.type',string='Supplement Type')
    price = fields.Float(string='Price')
    tree_link = fields.Many2one('offers.builder')

    
class SupplementTypeForm(models.Model):
    _name = 'supplement.type'
    _description = 'Supplement Type'
    _rec_name = 'name'

    name = fields.Char(string='Name')