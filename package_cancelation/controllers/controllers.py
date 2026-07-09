# -*- coding: utf-8 -*-
# from odoo import http


# class PackageCancelation(http.Controller):
#     @http.route('/package_cancelation/package_cancelation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/package_cancelation/package_cancelation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('package_cancelation.listing', {
#             'root': '/package_cancelation/package_cancelation',
#             'objects': http.request.env['package_cancelation.package_cancelation'].search([]),
#         })

#     @http.route('/package_cancelation/package_cancelation/objects/<model("package_cancelation.package_cancelation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('package_cancelation.object', {
#             'object': obj
#         })
