# -*- coding: utf-8 -*-
from odoo import http

class EusolSetPackageData(http.Controller):
    @http.route('/set/arrival_departure/dates', auth='public')
    def index(self, **kw):
        res = http.request.env['reservation.order'].set_arrival_departure_dates()
        return 'done'

    @http.route('/set/check_in_out/date/', auth='public')
    def index1(self, **kw):
        print ("11111111111111111111111111111111")
        res = http.request.env['reservation.order'].set_check_in_out_date()
        return 'done'

    @http.route('/set/invoice/dates/', auth='public')
    def index2(self, **kw):
        res = http.request.env['reservation.order'].set_invoice_dates()
        return 'done'

    @http.route('/set/payments/data/', auth='public')
    def index3(self, **kw):
        res = http.request.env['account.payment'].set_payments()
        return 'done'

    @http.route('/set/vendor_bills/data/', auth='public')
    def index4(self, **kw):
        res = http.request.env['reservation.order'].set_links_data()
        return 'done'

    @http.route('/set/e_tickets/data/', auth='public')
    def index5(self, **kw):
        res = http.request.env['all.services'].set_e_ticket_data()
        return 'done'
    @http.route('/set/aljazira_account/data/', auth='public')
    def index6(self, **kw):
        res = http.request.env['account.move.line'].set_accounts()
        return 'done'
    @http.route('/set/financial/terms/', auth='public')
    def index6(self, **kw):
        res = http.request.env['account.move'].set_financial_term()
        return 'done'
    @http.route('/set/package_line/link/', auth='public')
    def index7(self, **kw):
        res = http.request.env['reservation.order'].set_package_line_link()
        return 'done'
    @http.route('/set/amnt_fc/compute/', auth='public')
    def index8(self, **kw):
        res = http.request.env['account.move.line'].set_amnt_fc()
        return 'done'