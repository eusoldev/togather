#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved
# 
#    from num2words import num2words
#    import base64
#    import re
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api
import datetime
from datetime import date, datetime, timedelta
from datetime import date
import time
import calendar
from datetime import time
from dateutil.relativedelta import relativedelta
import datetime as dt




from bs4 import BeautifulSoup

import json


import requests



class quotation_builder_report(models.AbstractModel):
	_name = 'report.quotation_builder_report.quotation_builder_arabic'
	_description = "Report"

	@api.model
	def _get_report_values(self, docids, data=None):
		record = self.env['quotation.builder'].browse(docids)

		company = self.env['res.company'].search([('id','=',1)])

		return {
			'doc_ids': docids,
			'doc_model':'quotation.builder',
			'data': data,
			'docs': record,
			'company': company,
			'user_get': self.env.user.name,
			'creation_date': str(record.creation_date)[:-7],
			# 'destination_list': destination_list,
			# 'client_name': client_name,
			# 'ref': ref,
		}

class quotation_builder_english(models.AbstractModel):
	_name = 'report.quotation_builder_report.quotation_builder_report'
	_description = "Report"

	@api.model
	def _get_report_values(self, docids, data=None):
		record = self.env['quotation.builder'].browse(docids)

		company = self.env['res.company'].search([('id','=',1)])

		
		return {
			'doc_ids': docids,
			'doc_model':'quotation.builder',
			'data': data,
			'docs': record,
			'company': company,
			'user_get': self.env.user.name,
			'creation_date': str(record.creation_date)[:-7],
		}






class quotation_builder_english(models.AbstractModel):
	_name = 'report.quotation_builder_report.quotation_builder_email_t'
	_description = "Report Email"

	@api.model
	def _get_report_values(self, docids, data=None):
		record = self.env['quotation.builder'].browse(docids)

		company = self.env['res.company'].search([('id','=',1)])




		def google_maps_getting_email(self,req):
			ret = requests.get(req).text
			soup = BeautifulSoup(ret, features ='html.parser')
			img_listings = soup.find_all("img",class_="mimg vimgld") 
			img_url = 'https://i.ibb.co/6FZdJ6f/Maldives-featured.jpg'
			
			if img_listings:
				img_url = img_listings[0]['data-src']
				return img_url

			else:
				return img_url










		rooms_get_result = ''
		meals_get_result = ''
		transs_get_result = ''
		for link in record.tree_link_id:
			if link.room_type:
				rooms_get = ''
				for room in link.room_type:
					rooms_get += room.name + ', ' 
				result = ', '.join([s for s in rooms_get.split(', ') if s])
				rooms_get_result = result



			if link.meal_plane:
				meals_get=''
				for meal in link.meal_plane:
					meals_get += meal.name + ', ' 
				result = ', '.join([s for s in meals_get.split(', ') if s])
				meals_get_result = result



			if link.transfer:
				transs_get = ''
				for trans in link.transfer:
					transs_get += trans.name + ', ' 
				result = ', '.join([s for s in transs_get.split(', ') if s])
				transs_get_result = result




		print(rooms_get_result)
		print(meals_get_result)
		print(transs_get_result)




		total_len = len(record.tree_link_id)
		if record.tree_link_id:
			for get in record.tree_link_id:
				if get.resort_name:

					for x in get.resort_name:
					
						url = "https://www.bing.com/images/search?q="

						if x.company_type == 'company':
							if x.name:
								url += x.name.replace(' ','+')
							if x.street_name:
								url += x.street_name.replace(' ','+')
							if x.street2:
								url += x.street2.replace(' ','+')
							if x.street_number:
								url += x.street_number.replace(' ','+')
							if x.street_number2:
								url += x.street_number2.replace(' ','+')
							if x.city:
								url += '+'+x.city.replace(' ','+')
							if x.state_id:
								url += '+'+x.state_id.name.replace(' ','+')
							get_image_url = google_maps_getting_email(self,url)
							get.image_url = get_image_url

						else:
							if x.name:
								url += x.name.replace(' ','+')
							if x.ind_street:
								url += x.ind_street.replace(' ','+')
							if x.ind_street2:
								url += x.ind_street2.replace(' ','+')
							if x.ind_city:
								url += '+'+x.ind_city.replace(' ','+')
							if x.ind_state_id:
								url += '+'+x.ind_state_id.name.replace(' ','+')

							get_image_url = google_maps_getting_email(self,url)
							get.image_url = get_image_url

				else:
					pass



					


			

		
		return {
			'total_len' :total_len,
			'doc_ids': docids,
			'doc_model':'quotation.builder',
			'data': data,
			'docs': record,
			'company': company,
			'rooms_get_result': rooms_get_result,
			'meals_get_result': meals_get_result,
			'transs_get_result': transs_get_result,
		}