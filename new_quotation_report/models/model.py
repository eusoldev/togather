from odoo import models, fields, api
import datetime
from datetime import date, datetime, timedelta
from datetime import date
import time
import calendar
from datetime import time
from dateutil.relativedelta import relativedelta
import datetime as dt
import re

class new_quotation_report(models.AbstractModel):
	_name = 'report.new_quotation_report.new_quotation_report'
	_description = "New Quotation Report"




	# @api.constrains('terms_conditions_eng', 'cancel_new_eng')
	# def _validate_terms_conditions(self):
	#   for record in self:
	#       terms_lines = (record.terms_conditions_eng or '').splitlines()
	#       cancel_lines = (record.cancel_new_eng or '').splitlines()
	#       combined_lines = len(terms_lines) + len(cancel_lines)
			
	#       if combined_lines > 100:
	#           raise ValidationError("The combined length of terms and conditions and cancellation policies cannot exceed 100 lines.")

	@api.model
	def _get_report_values(self, docids, data=None):
		records = self.env['quotation.builder'].browse(docids)

		company = self.env['res.company'].search([],limit=1)


		same_records = []
		total_amount_new = 0
		for tree in records.tree_link_id:
			date = str(tree.check_in) + ' TO ' + str(tree.check_out)
			if date not in same_records:
				same_records.append(date)
				total_amount_new += tree.total

		diffrent_records = []
		for date in same_records:
			grouped_records = []
			total_cost = 0
			for tree in records.tree_link_id:
				tree_date = str(tree.check_in) + ' TO ' + str(tree.check_out)
				if tree_date == date:
					grouped_records.append(tree)
					total_cost += tree.total

			diffrent_records.append({
				'date': date,
				'grouped_records': grouped_records,
				'total_cost': total_cost,
			})
		print(diffrent_records)
		print('--------------------------------')
			

		def get_url(hotel_id):
			url = "http://maps.google.com/maps?oi=map&q="
			if hotel_id:
				if hotel_id.company_type == 'company':
					if hotel_id.name:
						url += hotel_id.name.replace(' ','+')
					if hotel_id.street_name:
						url += hotel_id.street_name.replace(' ','+')
					if hotel_id.street2:
						url += hotel_id.street2.replace(' ','+')
					if hotel_id.street_number:
						url += hotel_id.street_number.replace(' ','+')
					if hotel_id.street_number2:
						url += hotel_id.street_number2.replace(' ','+')
					if hotel_id.city:
						url += '+'+hotel_id.city.replace(' ','+')
					if hotel_id.state_id:
						url += '+'+hotel_id.state_id.name.replace(' ','+')
					if hotel_id.zip:
						url += '+'+hotel_id.zip.replace(' ','+')
					if hotel_id.country_id:
						url += '+'+hotel_id.country_id.name.replace(' ','+')
				else:
					if hotel_id.name:
						url += hotel_id.name.replace(' ','+')
					if hotel_id.ind_street:
						url += hotel_id.ind_street.replace(' ','+')
					if hotel_id.ind_street2:
						url += hotel_id.ind_street2.replace(' ','+')
					if hotel_id.ind_city:
						url += '+'+hotel_id.ind_city.replace(' ','+')
					if hotel_id.ind_state_id:
						url += '+'+hotel_id.ind_state_id.name.replace(' ','+')
					if hotel_id.ind_zip:
						url += '+'+hotel_id.ind_zip.replace(' ','+')
					if hotel_id.ind_country_id:
						url += '+'+hotel_id.ind_country_id.name.replace(' ','+')
			return url
						
		

		def is_html_empty(html_content):
			"""Check if a html content is empty. If there are only formatting tags or
			a void content return True. Famous use case if a '<p><br></p>' added by
			some web editor.

			:param str html_content: html content, coming from example from an HTML field
			:returns: bool, True if no content found or if containing only void formatting tags
			"""
			if not html_content:
				return True
			tag_re = re.compile(r'\<\s*\/?(?:p|div|span|br|b|i)\s*/?\s*\>')
			return not bool(re.sub(tag_re, '', html_content).strip())
	
		return {
			'doc_ids': docids,
			'doc_model':'quotation.builder',
			'docs': records,
			'company': company,
			'is_html_empty': is_html_empty,
			'get_url': get_url,
			'total_amount_new': total_amount_new,
			'diffrent_records': diffrent_records,

		}

	# @api.model
	# def _get_report_values(self, docids, data=None):
	#   docs = self.env['quotation.builder'].browse(docids)
	#   return {
	#       'doc_ids': docids,
	#       'doc_model': 'quotation.builder',
	#       'docs': docs,
	#   }


