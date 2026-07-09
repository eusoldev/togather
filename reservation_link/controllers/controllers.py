import logging
_logger = logging.getLogger(__name__)
import json
import os
import werkzeug.utils
from odoo import http, models, fields, _
from odoo.http import request
from odoo.addons.portal.controllers.web import Home
from odoo.exceptions import ValidationError, UserError

class EXTWebsiteR(http.Controller):


	@http.route('/reservation_link_web_view_ext/<sale_id>', type='http', auth="public", website=True, cache=300)
	def reservation_link_web_view_ext(self, sale_id,**opt):

		sale_rec = request.env['reservation.order'].sudo().search([('id', '=', int(sale_id))])
		if sale_rec:
			customer_m2m = []
			for x in sale_rec.itinarnay_package:
				for y in x.customer_m2m:
					if y not in customer_m2m:
						customer_m2m.append(y)
			if sale_rec.stages =="validate":

					return request.render("reservation_link.reservation_link_template", {
						'sale_rec':sale_rec,
						'customer_m2m':customer_m2m,
					})


			else:
				return request.render("reservation_link.reservation_link_template_not_found", {
				})
				raise ValidationError("No Sale Order against ID: "+sale_id)
		



		else:
			return request.render("reservation_link.reservation_link_template_not_found", {
			})
			raise ValidationError("No Sale Order against ID: "+sale_id)


	@http.route ( '/submit/note/sale_order' , type = "http" , auth = 'public' , methods = [ 'POST','GET' ] , website=True)
	def submit_note_sale_order (self , ** kw ):
		if request.httprequest.method == 'POST':
			msg = str(kw.get('msg'))
			sale_id = int(kw.get('sale_rec'))
			sale_rec = request.env['reservation.order'].sudo().search([('id', '=', int(sale_id))])
			if sale_rec:
				for x in sale_rec:
					x.customer_note = msg
			print(msg)
			print(sale_rec)

			return request.redirect('/reservation_link_web_view_ext/{}'.format(sale_id))


