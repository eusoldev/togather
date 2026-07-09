import logging
_logger = logging.getLogger(__name__)
import json
import os
import werkzeug.utils
from odoo import http, models, fields, _
from odoo.http import request
from odoo.addons.portal.controllers.web import Home
from odoo.exceptions import ValidationError, UserError
from bs4 import BeautifulSoup
import requests
from itertools import groupby
from datetime import datetime, date, timedelta





class EXTWebsiteR(http.Controller):

	def group_records_by_date_and_service_type(self, date_range, records):
		# Helper function to group records by date and service type
		grouped_records = {}
		for key in date_range:
			grouped_records[key] = {}  # Initialize an empty dictionary for each date

		for date, group in groupby(records, key=lambda x: self.get_date_field(x)):
			date_key = date
			nested_group = grouped_records.get(date_key, {})
			for record in group:
				service_type = record.service_type
				nested_group.setdefault(service_type, []).append(record)
			grouped_records[date_key] = nested_group

		return grouped_records

	def get_date_field(self, record):
		# Determine the appropriate date field based on service_type
		if record.service_type == 'hotel' and record.check_in:
			return record.check_in
		elif record.service_type == 'flight' and record.departures:
			return record.departures.date()
		elif record.service_type == 'tour' and record.ticket_day:
			return record.ticket_day
		elif record.service_type == 'other' and record.date_from:
			return record.date_from	
		else:
			return record.booking_date




	def get_date_range(self, creation_date, date_to):

		print(creation_date)
		print(date_to)
		date_range = []
		current_date = creation_date
		while current_date <= date_to:
			date_range.append(current_date)
			current_date += timedelta(days=1)
		return date_range

	@http.route('/quotation_builder_link_web_view/<sale_id>', type='http', auth="public", website=True, cache=300)
	def quotation_builder_link_web_view(self, sale_id, **opt):
		sale_rec = request.env['quotation.builder'].sudo().search([('id', '=', int(sale_id))])

		if sale_rec:
			creation_date = sale_rec.creation_date.date()
			date_to = sale_rec.date_to.date()
			date_range = self.get_date_range(creation_date, date_to)
			records = sale_rec.tree_link_id
			valid_records = [record for record in records if record.booking_date]
			grouped_records = self.group_records_by_date_and_service_type(date_range, valid_records)
			sorted_grouped_records = dict(sorted(grouped_records.items(), key=lambda x: (x[0].month, x[0].day)))
			print(sorted_grouped_records)

			if sale_rec.state == "validate":
				# Render the template with grouped records
				return request.render("quotation_builder.quotation_builder_link", {
					'grouped_records': sorted_grouped_records,
					'sale_rec': sale_rec
				})

			else:
				return request.render("quotation_builder.quotation_builder_link_template_not_found", {})
				raise ValidationError("No Sale Order against ID: " + sale_id)

		else:
			return request.render("quotation_builder.quotation_builder_link_template_not_found", {})
			raise ValidationError("No Sale Order against ID: " + sale_id)


	



	def google_maps_gettings(self, req):
		try:
			ret = requests.get(req).text
			print(req)
			print('333333333333333333333333')
			soup = BeautifulSoup(ret, features='html.parser')
			img_listings = soup.find_all("a", class_="iusc")
			img_listingss = soup.find_all("img", class_="mimg vimgld")
			img_url = 'https://i.ibb.co/6FZdJ6f/Maldives-featured.jpg'
			if img_listings:
				img_url2 = img_listings[0]['href']
				if img_url2:
					url2 = "https://www.bing.com"+str(img_url2)
					ret2 = requests.get(url2).text
					soup2 = BeautifulSoup(ret2, features='html.parser')
					img_listings2 = soup2.find_all("img")
					if img_listings2:
						if 'http' in img_listings2[0]['src']:
							img_url = img_listings2[0]['src']
						else:
							if img_listingss:
								if 'http' in img_listingss[0]['data-src']:
									img_url = img_listingss[0]['data-src']


			return img_url
		except Exception as e:
			return 'https://i.ibb.co/6FZdJ6f/Maldives-featured.jpg'
