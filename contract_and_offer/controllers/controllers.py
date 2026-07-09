# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.web.controllers.main import Binary

	# @http.route('/web/content/', auth='none', type='json', cors='*')
class ContractAndOffer(Binary):
	@http.route(['/web/content',
		'/web/content/<string:xmlid>',
		'/web/content/<string:xmlid>/<string:filename>',
		'/web/content/<int:id>',
		'/web/content/<int:id>/<string:filename>',
		'/web/content/<int:id>-<string:unique>',
		'/web/content/<int:id>-<string:unique>/<string:filename>',
		'/web/content/<int:id>-<string:unique>/<path:extra>/<string:filename>',
		'/web/content/<string:model>/<int:id>/<string:field>',
		'/web/content/<string:model>/<int:id>/<string:field>/<string:filename>'], type='http', auth="public", cors='*')
	def content_common(self, **kw):
		res = super(ContractAndOffer, self).content_common()
		return res

#     @http.route('/contract_and_offer/contract_and_offer/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('contract_and_offer.listing', {
#             'root': '/contract_and_offer/contract_and_offer',
#             'objects': http.request.env['contract_and_offer.contract_and_offer'].search([]),
#         })

#     @http.route('/contract_and_offer/contract_and_offer/objects/<model("contract_and_offer.contract_and_offer"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contract_and_offer.object', {
#             'object': obj
#         })