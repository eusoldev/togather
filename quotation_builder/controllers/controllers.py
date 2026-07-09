# -*- coding: utf-8 -*-
# from odoo import http


# class QuotationBuilder(http.Controller):
#     @http.route('/quotation_builder/quotation_builder/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/quotation_builder/quotation_builder/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('quotation_builder.listing', {
#             'root': '/quotation_builder/quotation_builder',
#             'objects': http.request.env['quotation_builder.quotation_builder'].search([]),
#         })

#     @http.route('/quotation_builder/quotation_builder/objects/<model("quotation_builder.quotation_builder"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('quotation_builder.object', {
#             'object': obj
#         })
