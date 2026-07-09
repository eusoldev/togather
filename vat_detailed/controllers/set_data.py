# -*- coding: utf-8 -*-
from odoo import http

class EusolSetVatCommissionData(http.Controller):
    @http.route('/set/commissioned/boolean', auth='public')
    def indexed(self, **kw):
        res = http.request.env['vat.detailed'].set_commissioned_field()
        return 'done'
    @http.route('/set/is_commissioned/boolean', auth='public')
    def index(self, **kw):
        res = http.request.env['vat.detailed'].set_jes()
        return 'done'
