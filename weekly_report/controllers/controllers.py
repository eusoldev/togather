# -*- coding: utf-8 -*-
# from odoo import http


# class WeeklyReport(http.Controller):
#     @http.route('/weekly_report/weekly_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/weekly_report/weekly_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('weekly_report.listing', {
#             'root': '/weekly_report/weekly_report',
#             'objects': http.request.env['weekly_report.weekly_report'].search([]),
#         })

#     @http.route('/weekly_report/weekly_report/objects/<model("weekly_report.weekly_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('weekly_report.object', {
#             'object': obj
#         })
