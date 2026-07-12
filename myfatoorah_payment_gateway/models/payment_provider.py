from odoo import api, fields, models


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('myfatoorah', "MyFatoorah")],
        ondelete={'myfatoorah': 'set default'},
        help="Select 'MyFatoorah' as the payment provider if you want to process payments through MyFatoorah."
    )

    myfatoorah_token = fields.Char(
        string='Token',
        help="Enter the authentication token required for integrating with MyFatoorah's payment gateway."
    )
    myfatoorah_payment_method_ids = fields.Char(
        string='Allowed Payment Method IDs',
        help="Optional comma-separated MyFatoorah PaymentMethodId values to limit which methods "
             "appear on the hosted payment page, for example: 2,6,11"
    )
    myfatoorah_enable_refund = fields.Boolean(
        string='Enable Refunds',
        help="Allow MyFatoorah full and partial refunds from Odoo."
    )
    myfatoorah_refund_service_charge_on_customer = fields.Boolean(
        string='Charge Service Fees On Customer',
        help="If enabled, MyFatoorah will charge the customer the service fees during refund processing."
    )
    myfatoorah_refund_require_otp = fields.Boolean(
        string='Require OTP For Refunds',
        help="Require a one-time password approval step before sending a MyFatoorah refund request."
    )
    myfatoorah_refund_otp_validity_minutes = fields.Integer(
        string='Refund OTP Validity (Minutes)',
        default=10,
        help="How long the refund OTP stays valid after being sent."
    )

    @api.depends('code', 'myfatoorah_enable_refund')
    def _compute_feature_support_fields(self):
        super()._compute_feature_support_fields()
        for provider in self.filtered(lambda p: p.code == 'myfatoorah'):
            provider.support_refund = 'partial' if provider.myfatoorah_enable_refund else 'none'

    def _myfatoorah_get_api_url(self):
        self.ensure_one()
        return 'https://api.myfatoorah.com/' if self.state == 'enabled' else 'https://apitest.myfatoorah.com/'

    def _myfatoorah_get_allowed_payment_method_ids(self):
        self.ensure_one()
        if not self.myfatoorah_payment_method_ids:
            return []
        method_ids = []
        for raw_value in self.myfatoorah_payment_method_ids.replace('\n', ',').split(','):
            raw_value = raw_value.strip()
            if not raw_value:
                continue
            if not raw_value.isdigit():
                continue
            method_ids.append(int(raw_value))
        return method_ids

    def _get_myfatoorah_refund_otp_users(self):
        self.ensure_one()
        group = self.env.ref('myfatoorah_payment_gateway.group_myfatoorah_refund_otp_approver')
        return group.users.filtered(lambda user: user.active and (user.email or user.partner_id.email))

    def _get_redirect_form_view(self, is_validation=False):
        self.ensure_one()
        if self.code == 'myfatoorah':
            return self.env.ref('myfatoorah_payment_gateway.redirect_form')
        return super()._get_redirect_form_view(is_validation)
