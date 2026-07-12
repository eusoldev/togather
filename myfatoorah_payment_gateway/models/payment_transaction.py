import json
import logging

import requests

from odoo import _, api, fields, models
from odoo.addons.payment import utils as payment_utils
from odoo.exceptions import AccessError, ValidationError
from odoo.tools import email_normalize_all, float_is_zero, format_amount

_logger = logging.getLogger(__name__)

# Common MyFatoorah payment method ids:
# - 1 = KNET
# - 2 = VISA/MASTER
# - 6 = MADA
# - 11 = Apple Pay
# - 14 = STC Pay

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    myfatoorah_link_description = fields.Char(string='MyFatoorah Link Description', readonly=True, copy=False)
    myfatoorah_payment_method_name = fields.Char(string='MyFatoorah Payment Method', readonly=True, copy=False)
    myfatoorah_send_payment_payload = fields.Text(string='MyFatoorah SendPayment Payload', readonly=True, copy=False)
    myfatoorah_send_payment_response = fields.Text(string='MyFatoorah SendPayment Response', readonly=True, copy=False)
    myfatoorah_status_response = fields.Text(string='MyFatoorah Status Response', readonly=True, copy=False)
    myfatoorah_invoice_url = fields.Char(string='MyFatoorah Invoice URL', readonly=True, copy=False)
    myfatoorah_invoice_id = fields.Char(string='MyFatoorah Invoice ID', readonly=True, copy=False)
    myfatoorah_refund_enabled = fields.Boolean(related='provider_id.myfatoorah_enable_refund')
    myfatoorah_refund_payload = fields.Text(string='MyFatoorah Refund Payload', readonly=True, copy=False)
    myfatoorah_refund_response = fields.Text(string='MyFatoorah Refund Response', readonly=True, copy=False)
    myfatoorah_refund_status_response = fields.Text(string='MyFatoorah Refund Status Response', readonly=True, copy=False)
    myfatoorah_refund_id = fields.Char(string='MyFatoorah Refund ID', readonly=True, copy=False)
    myfatoorah_refund_reference = fields.Char(string='MyFatoorah Refund Reference', readonly=True, copy=False)
    myfatoorah_refund_external_identifier = fields.Char(string='MyFatoorah Refund External Identifier', readonly=True, copy=False)
    myfatoorah_refund_comment = fields.Char(string='MyFatoorah Refund Comment', readonly=True, copy=False)
    myfatoorah_refund_amount_deducted_from_supplier = fields.Float(
        string='MyFatoorah Amount Deducted From Supplier', readonly=True, copy=False
    )

    @staticmethod
    def _myfatoorah_dump_json(value):
        return json.dumps(value or {}, indent=2, sort_keys=True)

    def _get_myfatoorah_provider(self):
        self.ensure_one()
        return self.provider_id

    @staticmethod
    def _get_partner_mobile_number(partner):
        if not partner:
            return ''
        if 'mobile' in partner._fields and partner.mobile:
            return partner.mobile
        return partner.phone or ''

    def _myfatoorah_make_request(self, endpoint, payload):
        self.ensure_one()
        provider = self._get_myfatoorah_provider()
        url = f"{provider._myfatoorah_get_api_url()}v2/{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {provider.myfatoorah_token}',
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        try:
            response_data = response.json()
        except ValueError as error:
            raise ValidationError(_("MyFatoorah returned an invalid response.")) from error

        if not response.ok:
            message = (
                response_data.get('Message')
                or response_data.get('message')
                or _("The communication with MyFatoorah failed.")
            )
            raise ValidationError(str(message))
        return response_data

    def _check_myfatoorah_refund_access(self):
        self.ensure_one()
        if self.provider_code != 'myfatoorah':
            return
        if not self.provider_id.myfatoorah_enable_refund:
            raise ValidationError(_("MyFatoorah refunds are disabled on this provider."))
        if not self.env.user.has_group('myfatoorah_payment_gateway.group_myfatoorah_refund_manager'):
            raise AccessError(_("You are not allowed to refund MyFatoorah transactions."))

    def _get_myfatoorah_refund_otp_users(self):
        self.ensure_one()
        otp_users = self.provider_id.sudo()._get_myfatoorah_refund_otp_users()
        if not otp_users:
            raise ValidationError(_("No user is currently available to receive refund OTP."))
        return otp_users

    def _get_myfatoorah_refund_otp_recipient_emails(self):
        self.ensure_one()
        recipients = []
        for user in self._get_myfatoorah_refund_otp_users():
            email = user.email or user.partner_id.email
            if email:
                recipients.append((user, email))
        if not recipients:
            raise ValidationError(_("No user is currently available to receive refund OTP."))
        return recipients

    @staticmethod
    def _get_myfatoorah_payment_identifier(notification_data):
        return (
            notification_data.get('paymentId')
            or notification_data.get('PaymentId')
            or notification_data.get('payment_id')
            or notification_data.get('Id')
            or notification_data.get('id')
        )

    def _get_myfatoorah_customer_partner(self):
        self.ensure_one()
        if 'invoice_ids' in self._fields and self.invoice_ids:
            partner = self.invoice_ids[:1].partner_id
            if partner:
                return partner
        return self.partner_id

    def _get_mobile_country_code(self, partner):
        self.ensure_one()
        countries = (
            partner.country_id
            or self.partner_country_id
            or self.provider_id.company_id.country_id
            or self.env.company.country_id
        )
        code = ''.join(char for char in str(countries.phone_code or '') if char.isdigit())
        return f"+{code}" if code else ''

    @staticmethod
    def _normalize_myfatoorah_mobile(phone_number, country_code):
        raw_number = (phone_number or '').strip()
        code = ''.join(char for char in str(country_code or '') if char.isdigit())
        number = ''.join(char for char in raw_number if char.isdigit())

        if not number:
            return code, ''

        if raw_number.startswith('00') and code and number.startswith(code):
            number = number[len(code):]
        elif code and number.startswith(code):
            number = number[len(code):]

        if number.startswith('00'):
            number = number[2:]

        if number.startswith('0'):
            number = number[1:]

        if len(number) > 11:
            if code and number.endswith(code):
                number = number[:-len(code)]
            number = number[-11:]

        return code, number

    def _get_myfatoorah_invoice_items(self):
        self.ensure_one()
        if self.myfatoorah_link_description:
            return [{
                'ItemName': (self.myfatoorah_link_description or self.reference or _("Payment"))[:100],
                'Quantity': 1,
                'UnitPrice': float(self.currency_id.round(self.amount or 0.0)),
            }]
        if 'invoice_ids' not in self._fields or not self.invoice_ids:
            return []

        currency = self.currency_id
        invoice_total_amount = 0.0
        invoice_items = []
        for invoice in self.invoice_ids:
            for line in invoice.invoice_line_ids.filtered(lambda l: not l.display_type or l.display_type == 'product'):
                line_total = float(currency.round(line.price_total or 0.0))
                if float_is_zero(line_total, precision_rounding=currency.rounding):
                    continue
                invoice_total_amount += line_total
                invoice_items.append({
                    'ItemName': (line.name or invoice.name or self.reference)[:100],
                    'Quantity': 1,
                    'UnitPrice': line_total,
                })

        transaction_amount = float(currency.round(self.amount or 0.0))
        if (
            invoice_items
            and not float_is_zero(invoice_total_amount, precision_rounding=currency.rounding)
            and float_is_zero(transaction_amount - invoice_total_amount, precision_rounding=currency.rounding)
        ):
            return invoice_items

        if invoice_items:
            _logger.info(
                "Skipping MyFatoorah InvoiceItems for transaction %s because payment amount %s "
                "does not match invoice total %s.",
                self.reference,
                transaction_amount,
                float(currency.round(invoice_total_amount)),
            )
        return []

    def _get_myfatoorah_refund_key(self):
        self.ensure_one()
        if self.myfatoorah_invoice_id:
            return 'InvoiceId', str(self.myfatoorah_invoice_id)
        if self.provider_reference:
            return 'PaymentId', str(self.provider_reference)
        raise ValidationError(_("No MyFatoorah payment or invoice reference was found for refunding."))

    def _get_myfatoorah_refund_child_transactions(self):
        self.ensure_one()
        return self.search([
            ('source_transaction_id', '=', self.id),
            ('operation', '=', 'refund'),
            ('provider_code', '=', 'myfatoorah'),
        ])

    def _get_myfatoorah_reserved_refund_amount(self):
        self.ensure_one()
        refund_txs = self._get_myfatoorah_refund_child_transactions().filtered(lambda tx: tx.state not in ('cancel', 'error'))
        return sum(abs(tx.amount) for tx in refund_txs)

    def _get_myfatoorah_remaining_refundable_amount(self):
        self.ensure_one()
        remaining_amount = float(self.currency_id.round((self.amount or 0.0) - self._get_myfatoorah_reserved_refund_amount()))
        return max(remaining_amount, 0.0)

    def _check_myfatoorah_refund_request_constraints(self, refund_amount, external_identifier=False):
        self.ensure_one()
        pending_refunds = self._get_myfatoorah_refund_child_transactions().filtered(
            lambda tx: tx.state not in ('done', 'cancel', 'error')
        )
        if pending_refunds:
            raise ValidationError(_(
                "A MyFatoorah refund request is already in progress for this transaction. "
                "Wait for it to complete before sending another refund."
            ))

        remaining_amount = self._get_myfatoorah_remaining_refundable_amount()
        if refund_amount > remaining_amount:
            raise ValidationError(_(
                "The requested refund amount exceeds the remaining refundable balance. "
                "Remaining amount: %(remaining)s.",
                remaining=format_amount(self.env, remaining_amount, self.currency_id),
            ))

        if external_identifier:
            duplicate_refund = self._get_myfatoorah_refund_child_transactions().filtered(
                lambda tx: (
                    tx.myfatoorah_refund_external_identifier == external_identifier
                    and tx.state not in ('cancel', 'error')
                )
            )[:1]
            if duplicate_refund:
                raise ValidationError(_(
                    "A refund with the same External Identifier already exists for this transaction."
                ))

    def _myfatoorah_fetch_refund_status(self):
        self.ensure_one()
        if self.provider_code != 'myfatoorah' or self.operation != 'refund':
            raise ValidationError(_("Refund status is only available for MyFatoorah refund transactions."))
        if self.myfatoorah_refund_id:
            payload = {'Key': str(self.myfatoorah_refund_id), 'KeyType': 'RefundId'}
        elif self.myfatoorah_refund_reference:
            payload = {'Key': str(self.myfatoorah_refund_reference), 'KeyType': 'RefundReference'}
        elif self.source_transaction_id and self.source_transaction_id.myfatoorah_invoice_id:
            payload = {'Key': str(self.source_transaction_id.myfatoorah_invoice_id), 'KeyType': 'InvoiceId'}
        else:
            raise ValidationError(_("No MyFatoorah refund reference is available to check refund status."))
        response_data = self._myfatoorah_make_request('GetRefundStatus', payload)
        self.write({'myfatoorah_refund_status_response': self._myfatoorah_dump_json(response_data)})
        return response_data

    def _apply_myfatoorah_refund_status(self, status_data):
        self.ensure_one()
        results = status_data.get('Data', {}).get('RefundStatusResult') or []
        if self.myfatoorah_refund_id:
            result = next((item for item in results if str(item.get('RefundId')) == str(self.myfatoorah_refund_id)), None)
        elif self.myfatoorah_refund_reference:
            result = next((item for item in results if str(item.get('RefundReference')) == str(self.myfatoorah_refund_reference)), None)
        else:
            result = results[-1] if results else None
        if not result:
            raise ValidationError(_("MyFatoorah did not return a refund status result for this refund request."))

        status = (result.get('RefundStatus') or '').lower()
        message_parts = [result.get('RefundStatus'), result.get('RefundReference'), result.get('RRN')]
        state_message = ' | '.join(part for part in message_parts if part)
        self.write({
            'myfatoorah_refund_id': str(result.get('RefundId') or self.myfatoorah_refund_id or ''),
            'myfatoorah_refund_reference': str(result.get('RefundReference') or self.myfatoorah_refund_reference or ''),
            'myfatoorah_refund_external_identifier': result.get('ExternalIdentifier') or self.myfatoorah_refund_external_identifier,
        })
        if status == 'refunded':
            self._set_done(state_message=state_message or None)
            self._post_process()
        elif status == 'pending':
            self._set_pending(state_message=state_message or None, extra_allowed_states=('done',))
        elif status in ('canceled', 'cancelled'):
            self._set_canceled(state_message=state_message or None, extra_allowed_states=('error',))
        else:
            self._set_error(
                state_message or _("Unable to determine the MyFatoorah refund status."),
                extra_allowed_states=('cancel', 'done'),
            )
        return result

    def _myfatoorah_fetch_payment_status(self, notification_data):
        self.ensure_one()
        payment_id = self._get_myfatoorah_payment_identifier(notification_data)
        if not payment_id:
            raise ValidationError(_("MyFatoorah callback did not include a payment id."))
        response_data = self._myfatoorah_make_request('GetPaymentStatus', {
            'Key': str(payment_id),
            'KeyType': 'paymentId',
        })
        self.write({
            'myfatoorah_status_response': self._myfatoorah_dump_json(response_data),
        })
        return response_data

    @staticmethod
    def _extract_myfatoorah_reference(status_data, notification_data):
        data = status_data.get('Data', {}) if status_data else {}
        transactions = data.get('InvoiceTransactions') or []
        transaction_data = transactions[0] if transactions else {}
        return (
            PaymentTransaction._get_myfatoorah_payment_identifier(notification_data)
            or transaction_data.get('PaymentId')
            or data.get('InvoiceId')
            or data.get('InvoiceReference')
            or data.get('CustomerReference')
            or False
        )

    @staticmethod
    def _extract_myfatoorah_state_message(status_data):
        data = status_data.get('Data', {}) if status_data else {}
        transactions = data.get('InvoiceTransactions') or []
        transaction_data = transactions[0] if transactions else {}
        status_parts = [
            data.get('InvoiceStatus'),
            transaction_data.get('TransactionStatus'),
            transaction_data.get('Error'),
        ]
        return ' | '.join(part for part in status_parts if part)

    @staticmethod
    def _extract_myfatoorah_payment_method_name(status_data):
        data = status_data.get('Data', {}) if status_data else {}
        transactions = data.get('InvoiceTransactions') or []
        transaction_data = transactions[0] if transactions else {}
        return (
            transaction_data.get('PaymentGateway')
            or transaction_data.get('PaymentMethod')
            or transaction_data.get('PaymentMethodEn')
            or transaction_data.get('CardBrand')
            or transaction_data.get('PaymentType')
            or data.get('PaymentGateway')
            or False
        )

    @api.model
    def _get_specific_create_values(self, provider_code, values):
        specific_values = super()._get_specific_create_values(provider_code, values)
        if provider_code != 'myfatoorah':
            return specific_values

        invoice_commands = values.get('invoice_ids')
        if not invoice_commands or 'invoice_ids' not in self._fields:
            return specific_values

        invoice_ids = self._fields['invoice_ids'].convert_to_cache(invoice_commands, self)
        invoice = self.env['account.move'].browse(invoice_ids[:1]).exists()
        if not invoice:
            return specific_values

        partner = invoice.partner_id
        partner_emails = email_normalize_all(partner.email)
        return {
            **specific_values,
            'partner_id': partner.id,
            'partner_name': partner.name or partner.parent_id.name,
            'partner_lang': partner.lang,
            'partner_email': partner_emails[0] if partner_emails else None,
            'partner_address': payment_utils.format_partner_address(partner.street, partner.street2),
            'partner_zip': partner.zip,
            'partner_city': partner.city,
            'partner_state_id': partner.state_id.id,
            'partner_country_id': partner.country_id.id,
            'partner_phone': self._get_partner_mobile_number(partner),
        }

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'myfatoorah':
            return res
        return self.send_payment()

    def send_payment(self, notification_option='LNK'):
        self.ensure_one()
        odoo_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        partner = self._get_myfatoorah_customer_partner()
        mobile_country_code, phone_number = self._normalize_myfatoorah_mobile(
            self._get_partner_mobile_number(partner) or self.partner_phone,
            self._get_mobile_country_code(partner),
        )
        customer_email = partner.email or self.partner_email
        if not mobile_country_code or not phone_number:
            raise ValidationError(_("MyFatoorah requires a valid customer mobile number."))
        if notification_option in ('EML', 'ALL') and not customer_email:
            raise ValidationError(_("Please provide a customer email address."))

        currency = self.currency_id
        sendpay_data = {
            "NotificationOption": notification_option,
            "CustomerName": partner.name or self.partner_name,
            "DisplayCurrencyIso": currency.name,
            "InvoiceValue": float(currency.round(self.amount or 0.0)),
            "CallBackUrl": f"{odoo_base_url}/payment/myfatoorah/_return_url",
            "ErrorUrl": f"{odoo_base_url}/payment/myfatoorah/failed",
            "Language": "en",
            "CustomerReference": self.reference,
            "CustomerAddress": {
                "Address": partner.contact_address or self.partner_address or "",
            },
        }
        if mobile_country_code and phone_number:
            sendpay_data["MobileCountryCode"] = mobile_country_code
            sendpay_data["CustomerMobile"] = phone_number
        if customer_email:
            sendpay_data["CustomerEmail"] = customer_email
        allowed_method_ids = self.provider_id._myfatoorah_get_allowed_payment_method_ids()
        if allowed_method_ids:
            sendpay_data["InvoicePaymentMethods"] = allowed_method_ids
        invoice_items = self._get_myfatoorah_invoice_items()
        if invoice_items:
            sendpay_data["InvoiceItems"] = invoice_items
        self.write({
            'myfatoorah_send_payment_payload': self._myfatoorah_dump_json(sendpay_data),
        })
        try:
            response_data = self._myfatoorah_make_request('SendPayment', sendpay_data)
        except ValidationError as error:
            if sendpay_data.get("InvoiceItems"):
                _logger.warning(
                    "MyFatoorah rejected detailed InvoiceItems for transaction %s. "
                    "Retrying with amount-only payload. Error: %s",
                    self.reference,
                    error,
                )
                fallback_payload = dict(sendpay_data)
                fallback_payload.pop("InvoiceItems", None)
                self.write({
                    'myfatoorah_send_payment_payload': self._myfatoorah_dump_json(fallback_payload),
                })
                response_data = self._myfatoorah_make_request('SendPayment', fallback_payload)
            else:
                raise
        self.write({
            'myfatoorah_send_payment_response': self._myfatoorah_dump_json(response_data),
        })
        if not response_data.get('IsSuccess'):
            validation_errors = response_data.get('ValidationErrors')
            if validation_errors:
                error_message = validation_errors[0].get('Error')
                raise ValidationError(error_message)
        payment_url = response_data.get('Data', {}).get('InvoiceURL')
        if not payment_url:
            raise ValidationError(_("MyFatoorah did not return a payment URL."))
        self.write({
            'myfatoorah_invoice_id': str(response_data.get('Data', {}).get('InvoiceId') or ''),
            'myfatoorah_invoice_url': payment_url,
        })
        return {
            'payment_url': payment_url,
            'invoice_id': response_data.get('Data', {}).get('InvoiceId'),
        }

    @api.model
    def _search_by_reference(self, provider_code, payment_data):
        tx = super()._search_by_reference(provider_code, payment_data)
        if provider_code != 'myfatoorah' or tx:
            return tx

        payment_id = self._get_myfatoorah_payment_identifier(payment_data)
        if not payment_id:
            return tx

        tx_for_status = self.search([('provider_code', '=', 'myfatoorah')], limit=1)
        if not tx_for_status:
            return tx

        response_data = tx_for_status._myfatoorah_fetch_payment_status(payment_data)
        domain = [('provider_code', '=', 'myfatoorah')]
        reference = response_data.get('Data', {}).get('CustomerReference')
        invoice_id = response_data.get('Data', {}).get('InvoiceId')
        if reference:
            domain.append(('reference', '=', str(reference)))
        elif invoice_id:
            domain.append(('myfatoorah_invoice_id', '=', str(invoice_id)))
        else:
            return tx

        tx = self.search(domain, limit=1)
        if not tx:
            raise ValidationError(_(
                "No transaction found matching reference %s.",
                reference or invoice_id,
            ))
        return tx

    def _extract_amount_data(self, payment_data):
        if self.provider_code != 'myfatoorah':
            return super()._extract_amount_data(payment_data)
        return None

    def _apply_updates(self, payment_data):
        if self.provider_code != 'myfatoorah':
            return super()._apply_updates(payment_data)

        status_data = self._myfatoorah_fetch_payment_status(payment_data)
        data = status_data.get('Data', {})
        invoice_status = (data.get('InvoiceStatus') or '').lower()
        transactions = data.get('InvoiceTransactions') or []
        transaction_data = transactions[0] if transactions else {}
        transaction_status = (transaction_data.get('TransactionStatus') or '').lower()
        state_message = self._extract_myfatoorah_state_message(status_data)
        provider_reference = self._extract_myfatoorah_reference(status_data, payment_data)
        payment_method_name = self._extract_myfatoorah_payment_method_name(status_data)
        if provider_reference:
            self.provider_reference = str(provider_reference)
        if payment_method_name:
            self.myfatoorah_payment_method_name = str(payment_method_name)

        if transaction_status in ('success', 'succeeded', 'paid') or invoice_status in ('paid', 'success'):
            self._set_done(state_message=state_message or None)
        elif transaction_status in ('failed', 'declined', 'error'):
            self._set_error(
                state_message or _("The MyFatoorah payment attempt failed.")
            )
        elif transaction_status in ('canceled', 'cancelled'):
            self._set_canceled(state_message=state_message or None)
        elif transaction_status in ('pending',) or invoice_status in ('pending',):
            self._set_pending(state_message=state_message or None, extra_allowed_states=('done',))
        elif invoice_status in ('expired', 'failed', 'canceled', 'cancelled'):
            self._set_canceled(state_message=state_message or None)
        else:
            self._set_error(
                state_message or _("Unable to determine the MyFatoorah payment status.")
            )

    def action_open_myfatoorah_refund_wizard(self):
        self.ensure_one()
        self._check_myfatoorah_refund_access()
        if self.provider_code != 'myfatoorah':
            raise ValidationError(_("This refund action is only available for MyFatoorah transactions."))
        if self.state != 'done':
            raise ValidationError(_("Only confirmed MyFatoorah transactions can be refunded."))
        if self.operation == 'refund':
            raise ValidationError(_("Refund transactions cannot be refunded again from this action."))
        if not self.payment_id:
            raise ValidationError(_("No posted Odoo payment is linked to this transaction."))
        return {
            'name': _("Refund"),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'payment.refund.wizard',
            'target': 'new',
            'context': {
                'active_model': 'account.payment',
                'active_id': self.payment_id.id,
                'default_payment_id': self.payment_id.id,
            },
        }

    def action_sync_myfatoorah_refund_status(self):
        self.ensure_one()
        self._check_myfatoorah_refund_access()
        if self.provider_code != 'myfatoorah' or self.operation != 'refund':
            raise ValidationError(_("This action is only available for MyFatoorah refund transactions."))
        status_data = self._myfatoorah_fetch_refund_status()
        self._apply_myfatoorah_refund_status(status_data)
        return True

    def _refund(self, amount_to_refund=None):
        self.ensure_one()
        if self.provider_code != 'myfatoorah':
            return super()._refund(amount_to_refund=amount_to_refund)

        self._check_myfatoorah_refund_access()
        if self.provider_id.myfatoorah_refund_require_otp and not self.env.context.get('myfatoorah_refund_otp_verified'):
            raise ValidationError(_("Refund OTP verification is required before requesting a MyFatoorah refund."))
        self._ensure_provider_is_not_disabled()
        if self.state != 'done':
            raise ValidationError(_("Only confirmed MyFatoorah transactions can be refunded."))
        if self.operation == 'refund':
            raise ValidationError(_("A refund transaction cannot be refunded again."))

        refund_amount = abs(float(self.currency_id.round(amount_to_refund or self.amount)))
        if refund_amount <= 0:
            raise ValidationError(_("The refund amount must be positive."))
        amount_deducted_from_supplier = float(
            self.currency_id.round(self.env.context.get('myfatoorah_amount_deducted_from_supplier') or 0.0)
        )
        if amount_deducted_from_supplier < 0:
            raise ValidationError(_("Amount Deducted From Supplier cannot be negative."))
        if amount_deducted_from_supplier > refund_amount:
            raise ValidationError(_("Amount Deducted From Supplier cannot exceed the refund amount."))
        external_identifier = self.env.context.get('myfatoorah_refund_external_identifier') or False
        self._check_myfatoorah_refund_request_constraints(refund_amount, external_identifier=external_identifier)

        refund_tx = self._create_child_transaction(
            refund_amount,
            is_refund=True,
            myfatoorah_refund_comment=self.env.context.get('myfatoorah_refund_comment') or _("Refund for %s", self.reference),
            myfatoorah_refund_external_identifier=external_identifier,
            myfatoorah_refund_amount_deducted_from_supplier=amount_deducted_from_supplier,
        )
        key_type, key = self._get_myfatoorah_refund_key()
        payload = {
            'KeyType': key_type,
            'Key': key,
            'Amount': refund_amount,
            'Comment': refund_tx.myfatoorah_refund_comment or '',
            'ServiceChargeOnCustomer': bool(self.provider_id.myfatoorah_refund_service_charge_on_customer),
            'AmountDeductedFromSupplier': amount_deducted_from_supplier,
        }
        if refund_tx.myfatoorah_refund_external_identifier:
            payload['ExternalIdentifier'] = refund_tx.myfatoorah_refund_external_identifier
        refund_tx.write({'myfatoorah_refund_payload': self._myfatoorah_dump_json(payload)})
        response_data = self._myfatoorah_make_request('MakeRefund', payload)
        refund_tx.write({
            'myfatoorah_refund_response': self._myfatoorah_dump_json(response_data),
            'myfatoorah_refund_id': str(response_data.get('Data', {}).get('RefundId') or ''),
            'myfatoorah_refund_reference': str(response_data.get('Data', {}).get('RefundReference') or ''),
            'myfatoorah_refund_external_identifier': response_data.get('Data', {}).get('ExternalIdentifier') or refund_tx.myfatoorah_refund_external_identifier,
        })
        refund_tx._log_sent_message()
        status_data = refund_tx._myfatoorah_fetch_refund_status()
        refund_tx._apply_myfatoorah_refund_status(status_data)
        return refund_tx

    def _create_payment(self, **extra_create_values):
        payment = super()._create_payment(**extra_create_values)
        if self.provider_code == 'myfatoorah' and payment and self.myfatoorah_payment_method_name:
            memo_parts = [payment.memo or '', self.myfatoorah_payment_method_name]
            payment.memo = ' - '.join(part for part in memo_parts if part)
        return payment
