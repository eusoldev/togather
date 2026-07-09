# -*- coding: utf-8 -*-
# from odoo import http


# class MailTracking(http.Controller):
#     @http.route('/mail_tracking/mail_tracking/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mail_tracking/mail_tracking/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mail_tracking.listing', {
#             'root': '/mail_tracking/mail_tracking',
#             'objects': http.request.env['mail_tracking.mail_tracking'].search([]),
#         })

#     @http.route('/mail_tracking/mail_tracking/objects/<model("mail_tracking.mail_tracking"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mail_tracking.object', {
#             'object': obj
#         })
