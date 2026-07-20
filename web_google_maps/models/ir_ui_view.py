# -*- coding: utf-8 -*-
# License AGPL-3
from odoo import fields, models


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('google_map', 'Google Maps')])

    def _is_qweb_based_view(self, view_type):
        return super()._is_qweb_based_view(view_type) or view_type == 'google_map'

    def _get_view_info(self):
        return {'google_map': {'icon': 'fa fa-map-o'}} | super()._get_view_info()
