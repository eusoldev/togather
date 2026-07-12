import logging
import pprint
import json

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class PaymentMyFatoorahController(http.Controller):
    _return_url = '/payment/myfatoorah/_return_url'

    @http.route('/payment/myfatoorah/response', type='http', auth='public',
                website=True, methods=['POST'], csrf=False, save_session=False)
    def myfatoorah_payment_response(self, **data):
        """Redirect directly to the hosted MyFatoorah payment page."""
        payment_data = json.loads(data["data"])
        payment_url = payment_data.get("InvoiceURL")
        if not payment_url:
            return request.redirect('/payment/myfatoorah/failed')
        return request.redirect(payment_url)

    @http.route(_return_url, type='http', auth='public', methods=['GET'])
    def myfatoorah_checkout(self, **data):
        """ Function to redirect to the payment checkout"""
        _logger.info("Received MyFatoorah return data:\n%s",
                     pprint.pformat(data))
        tx_sudo = request.env['payment.transaction'].sudo()._search_by_reference(
            'myfatoorah', data
        )
        if tx_sudo:
            tx_sudo._process('myfatoorah', data)
        return request.redirect('/payment/status')

    @http.route('/payment/myfatoorah/failed', type='http', auth='public',
                website=True)
    def payment_failed(self, **data):
        """Process failed/cancelled returns and redirect to the payment status page."""
        _logger.info("Received MyFatoorah failure data:\n%s", pprint.pformat(data))
        payment_id = (
            data.get('paymentId')
            or data.get('PaymentId')
            or data.get('payment_id')
            or data.get('Id')
            or data.get('id')
        )
        if payment_id:
            try:
                tx_sudo = request.env['payment.transaction'].sudo()._search_by_reference(
                    'myfatoorah', data
                )
                if tx_sudo:
                    tx_sudo._process('myfatoorah', data)
                return request.redirect('/payment/status')
            except Exception:
                _logger.exception("Failed to process MyFatoorah failure callback for %s", payment_id)
        return request.render(
            "myfatoorah_payment_gateway.myfatoorah_payment_gateway_failed_form")
