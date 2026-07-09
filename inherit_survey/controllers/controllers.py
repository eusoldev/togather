# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.survey.controllers.main import Survey
import string 
import random
from odoo import http, SUPERUSER_ID


class SurveyEXT(Survey):


	@http.route('/survey/start/<string:survey_token>', type='http', auth='public', website=True)
	def survey_start(self, survey_token, answer_token=None, email=False, **post):
		""" Start a survey by providing
		 * a token linked to a survey;
		 * a token linked to an answer or generate a new token if access is allowed;
		"""
		access_data = self._get_access_data(survey_token, answer_token, ensure_token=False)
		if access_data['validity_code'] is not True:
			return self._redirect_with_error(access_data, access_data['validity_code'])

		survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']
		if not answer_sudo:
			try:
				answer_sudo = survey_sudo._create_answer(user=request.env.user, email=email)
			except UserError:
				answer_sudo = False

		if not answer_sudo:
			try:
				survey_sudo.with_user(request.env.user).check_access_rights('read')
				survey_sudo.with_user(request.env.user).check_access_rule('read')
			except:
				return werkzeug.utils.redirect("/")
			else:
				return request.render("survey.403", {'survey': survey_sudo})

		# Select the right page
		if answer_sudo.state == 'new':  # Intro page
			data = {'survey': survey_sudo, 'answer': answer_sudo, 'page': 0 , 'company_id':request.env.user.company_id}
			return request.render('survey.survey_fill_form_start', data)
		else:
			return request.redirect('/survey/fill/%s/%s' % (survey_sudo.access_token, answer_sudo.token))

		return super(SurveyEXT, self).survey_start(*args, **kwargs)

	@http.route('/survey/fill/<string:survey_token>/<string:answer_token>', type='http', auth='public', website=True)
	def survey_display_page(self, survey_token, answer_token, prev=None, **post):
		access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)
		if access_data['validity_code'] is not True:
			return self._redirect_with_error(access_data, access_data['validity_code'])

		survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']

		if survey_sudo.is_time_limited and not answer_sudo.start_datetime:
			# init start date when user starts filling in the survey
			answer_sudo.write({
				'start_datetime': fields.Datetime.now()
			})

		page_or_question_key = 'question' if survey_sudo.questions_layout == 'page_per_question' else 'page'
		# Select the right page
		if answer_sudo.state == 'new':  # First page
			page_or_question_id, last = survey_sudo.next_page_or_question(answer_sudo, 0, go_back=False)
			data = {
				'survey': survey_sudo,
				page_or_question_key: page_or_question_id,
				'answer': answer_sudo,
				'company_id':request.env.user.company_id

			}
			if last:
				data.update({'last': True,'company_id':request.env.user.company_id})
			return request.render('survey.survey', data)
		elif answer_sudo.state == 'done':  # Display success message
			return request.render('survey.sfinished', self._prepare_survey_finished_values(survey_sudo, answer_sudo))
		elif answer_sudo.state == 'skip':
			flag = (True if prev and prev == 'prev' else False)
			page_or_question_id, last = survey_sudo.next_page_or_question(answer_sudo, answer_sudo.last_displayed_page_id.id, go_back=flag)

			#special case if you click "previous" from the last page, then leave the survey, then reopen it from the URL, avoid crash
			if not page_or_question_id:
				page_or_question_id, last = survey_sudo.next_page_or_question(answer_sudo, answer_sudo.last_displayed_page_id.id, go_back=True)

			data = {
				'survey': survey_sudo,
				page_or_question_key: page_or_question_id,
				'answer': answer_sudo,
				'company_id':request.env.user.company_id
			}
			if last:
				data.update({'last': True})

			return request.render('survey.survey', data)
		else:
			return request.render("survey.403", {'survey': survey_sudo})


		return super(SurveyEXT, self).survey_display_page(*args, **kwargs)

	@http.route('/survey/fill/<string:survey_token>/<string:answer_token>', type='http', auth='public', website=True)
	def survey_display_page(self, survey_token, answer_token, prev=None, **post):
		access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)
		if access_data['validity_code'] is not True:
			return self._redirect_with_error(access_data, access_data['validity_code'])

		survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']

		if survey_sudo.is_time_limited and not answer_sudo.start_datetime:
			# init start date when user starts filling in the survey
			answer_sudo.write({
				'start_datetime': fields.Datetime.now()
			})

		page_or_question_key = 'question' if survey_sudo.questions_layout == 'page_per_question' else 'page'
		# Select the right page
		if answer_sudo.state == 'new':  # First page
			page_or_question_id, last = survey_sudo.next_page_or_question(answer_sudo, 0, go_back=False)
			data = {
				'survey': survey_sudo,
				page_or_question_key: page_or_question_id,
				'answer': answer_sudo,
				'company_id':request.env.user.company_id

			}
			if last:
				data.update({'last': True,'company_id':request.env.user.company_id})
			return request.render('survey.survey', data)
		elif answer_sudo.state == 'done':  # Display success message
			return request.render('survey.sfinished', self._prepare_survey_finished_values(survey_sudo, answer_sudo))
		elif answer_sudo.state == 'skip':
			flag = (True if prev and prev == 'prev' else False)
			page_or_question_id, last = survey_sudo.next_page_or_question(answer_sudo, answer_sudo.last_displayed_page_id.id, go_back=flag)

			#special case if you click "previous" from the last page, then leave the survey, then reopen it from the URL, avoid crash
			if not page_or_question_id:
				page_or_question_id, last = survey_sudo.next_page_or_question(answer_sudo, answer_sudo.last_displayed_page_id.id, go_back=True)

			data = {
				'survey': survey_sudo,
				page_or_question_key: page_or_question_id,
				'answer': answer_sudo,
				'company_id':request.env.user.company_id

			}
			if last:
				data.update({'last': True,'company_id':request.env.user.company_id})

			return request.render('survey.survey', data)
		else:
			return request.render("survey.403", {'survey': survey_sudo})



		return super(SurveyEXT, self).survey_display_page(*args, **kwargs)

	def _prepare_survey_finished_values(self, survey, answer, token=False):
		values = {'survey': survey, 'answer': answer,'company_id':request.env.user.company_id}
		if token:
			values['token'] = token
		if survey.scoring_type != 'no_scoring' and survey.certificate:
			answer_perf = survey._get_answers_correctness(answer)[answer]
			values['graph_data'] = json.dumps([
				{"text": "Correct", "count": answer_perf['correct']},
				{"text": "Partially", "count": answer_perf['partial']},
				{"text": "Incorrect", "count": answer_perf['incorrect']},
				{"text": "Unanswered", "count": answer_perf['skipped']}
			])
		return values


	@http.route('/survey/print/<string:survey_token>', type='http', auth='public', website=True, sitemap=False)
	def survey_print(self, survey_token, review=False, answer_token=None, **post):
		'''Display an survey in printable view; if <answer_token> is set, it will
		grab the answers of the user_input_id that has <answer_token>.'''
		access_data = self._get_access_data(survey_token, answer_token, ensure_token=False)
		if access_data['validity_code'] is not True and (
				access_data['has_survey_access'] or
				access_data['validity_code'] not in ['token_required', 'survey_closed', 'survey_void', 'answer_done']):
			return self._redirect_with_error(access_data, access_data['validity_code'])

		survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']

		return request.render('survey.survey_print', {
			'review': review,
			'survey': survey_sudo,
			'company_id':request.env.user.company_id,
			'answer': answer_sudo if survey_sudo.scoring_type != 'scoring_without_answers' else answer_sudo.browse(),
			'page_nr': 0,
			'quizz_correction': survey_sudo.scoring_type != 'scoring_without_answers' and answer_sudo})

	@http.route('/survey/results/<model("survey.survey"):survey>', type='http', auth='user', website=True)
	def survey_report(self, survey, answer_token=None, **post):
		'''Display survey Results & Statistics for given survey.'''
		result_template = 'survey.result'
		current_filters = []
		filter_display_data = []
		filter_finish = False

		answers = survey.user_input_ids.filtered(lambda answer: answer.state != 'new' and not answer.test_entry)
		if 'finished' in post:
			post.pop('finished')
			filter_finish = True
		if post or filter_finish:
			filter_data = self._get_filter_data(post)
			current_filters = survey.filter_input_ids(filter_data, filter_finish)
			filter_display_data = survey.get_filter_display_data(filter_data)
		return request.render(result_template,
									  {'survey': survey,
										'company_id':request.env.user.company_id,
									   'answers': answers,
									   'survey_dict': self._prepare_result_dict(survey, current_filters),
									   'page_range': self.page_range,
									   'current_filters': current_filters,
									   'filter_display_data': filter_display_data,
									   'filter_finish': filter_finish
									   })