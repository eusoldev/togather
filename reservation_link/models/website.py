# -*- coding: utf-8 -*-
from markupsafe import Markup

from odoo import models


class Website(models.Model):
	_inherit = 'website'

	def _control_third_party_trackers_in_html(self, html):
		return Markup(html or '')
