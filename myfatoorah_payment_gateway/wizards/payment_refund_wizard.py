from datetime import timedelta
import secrets

from markupsafe import Markup, escape

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import format_amount


class PaymentRefundWizard(models.TransientModel):
    _inherit = 'payment.refund.wizard'

    is_myfatoorah_refund = fields.Boolean(compute='_compute_is_myfatoorah_refund')
    myfatoorah_require_otp = fields.Boolean(compute='_compute_is_myfatoorah_refund')
    myfatoorah_refund_comment = fields.Char(string='Refund Comment')
    myfatoorah_refund_external_identifier = fields.Char(string='External Identifier')
    myfatoorah_amount_deducted_from_supplier = fields.Monetary(
        string='Amount Deducted From Supplier', currency_field='currency_id'
    )
    myfatoorah_remaining_refundable_amount = fields.Monetary(
        string='Remaining Refundable Amount',
        currency_field='currency_id',
        compute='_compute_myfatoorah_remaining_refundable_amount',
    )
    myfatoorah_otp_code = fields.Char(string='Generated OTP')
    myfatoorah_otp_expires_at = fields.Datetime(string='OTP Expires At')
    myfatoorah_otp_sent = fields.Boolean(string='OTP Sent')
    myfatoorah_otp_sent_to = fields.Char(string='OTP Sent To')
    myfatoorah_otp_input = fields.Char(string='Enter OTP')

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        payment = self.env['account.payment'].browse(
            values.get('payment_id') or self.env.context.get('default_payment_id') or self.env.context.get('active_id')
        )
        if payment:
            values.update(payment._get_payment_refund_wizard_values())
        return values

    def _compute_is_myfatoorah_refund(self):
        for wizard in self:
            wizard.is_myfatoorah_refund = wizard.transaction_id.provider_code == 'myfatoorah'
            wizard.myfatoorah_require_otp = bool(
                wizard.is_myfatoorah_refund and wizard.transaction_id.provider_id.myfatoorah_refund_require_otp
            )

    @api.depends('transaction_id')
    def _compute_myfatoorah_remaining_refundable_amount(self):
        for wizard in self:
            if wizard.transaction_id.provider_code == 'myfatoorah':
                wizard.myfatoorah_remaining_refundable_amount = (
                    wizard.transaction_id._get_myfatoorah_remaining_refundable_amount()
                )
            else:
                wizard.myfatoorah_remaining_refundable_amount = 0.0

    def _build_myfatoorah_otp_email_html(self, requester_name, transaction_ref, amount_text, otp_code, validity_minutes, user):
        self.ensure_one()
        company = self.transaction_id.company_id or self.env.company
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        company_name = company.name or _("Our Company")
        company_logo_url = f"{base_url}/web/image/res.company/{company.id}/logo" if company.id else ''
        company_phone = company.phone or company.partner_id.phone or ''
        company_email = company.email or company.partner_id.email or ''
        company_website = company.website or base_url
        company_address = company.partner_id.contact_address or ''
        refund_amount = amount_text
        refund_type = _("Partial Refund") if self.amount_to_refund < self.payment_amount else _("Full Refund")
        validity_text = _("%s minute(s)") % validity_minutes

        return Markup("""
<div style="margin:0;padding:24px 12px;background-color:#f4f6f8;font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;color:#1f2937;">
  <div style="max-width:640px;margin:0 auto;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 8px 24px rgba(15,23,42,0.08);">
    <div style="background:linear-gradient(135deg,#0f766e,#0ea5e9);padding:28px 24px;color:#ffffff;">
      <div style="margin-bottom:18px;">
        <img src="%s" alt="%s" style="max-width:180px;max-height:64px;width:auto;height:auto;display:block;"/>
      </div>
      <div style="font-size:24px;font-weight:700;line-height:1.3;">%s</div>
      <div style="margin-top:8px;font-size:15px;line-height:1.6;opacity:0.95;">%s</div>
    </div>
    <div style="padding:24px;">
      <div style="margin-bottom:18px;border-left:4px solid #0ea5e9;background:#eff6ff;padding:14px 16px;border-radius:10px;">
        <div style="font-size:15px;font-weight:700;color:#0f172a;">%s</div>
        <div style="margin-top:6px;font-size:13px;line-height:1.7;color:#475569;">
          %s<br/>
          %s<br/>
          %s<br/>
          %s
        </div>
      </div>
      <div style="border:1px solid #e5e7eb;border-radius:12px;padding:18px 16px;background:#f8fafc;">
        <div style="font-size:13px;color:#6b7280;margin-bottom:6px;">%s</div>
        <div style="font-size:22px;font-weight:700;color:#111827;">%s</div>
        <div style="margin-top:14px;font-size:14px;line-height:1.8;">
          <div><strong>%s</strong> %s</div>
          <div><strong>%s</strong> %s</div>
          <div><strong>%s</strong> %s</div>
          <div><strong>%s</strong> %s</div>
        </div>
      </div>
      <div style="margin:24px 0 20px;text-align:center;">
        <div style="display:inline-block;background:#111827;color:#ffffff;font-weight:700;font-size:28px;letter-spacing:6px;padding:16px 24px;border-radius:12px;">
          %s
        </div>
      </div>
      <div style="font-size:13px;color:#6b7280;line-height:1.7;word-break:break-word;">
        %s<br/>
        %s
      </div>
      <div style="margin-top:24px;padding-top:18px;border-top:1px solid #e5e7eb;font-size:12px;line-height:1.8;color:#64748b;text-align:center;">
        <div style="font-weight:700;color:#334155;">%s</div>
        <div>%s</div>
        <div>%s | %s</div>
      </div>
    </div>
  </div>
</div>
        """) % (
            escape(company_logo_url),
            escape(company_name),
            escape(_("MyFatoorah Refund OTP")),
            escape(_("Approve the refund only after confirming the request details below.")),
            escape(_("Refund Approval Request")),
            escape(company_address or _("Address not specified")),
            escape(company_phone or _("Phone not specified")),
            escape(company_email or _("Email not specified")),
            escape(company_website or base_url),
            escape(_("Refund Details")),
            escape(refund_amount),
            escape(_("Requested By:")),
            escape(requester_name),
            escape(_("Transaction:")),
            escape(transaction_ref),
            escape(_("Refund Type:")),
            escape(refund_type),
            escape(_("Valid For:")),
            escape(validity_text),
            escape(otp_code),
            escape(_("This OTP was sent to %(user)s and expires in %(mins)s minute(s).", user=user.name, mins=validity_minutes)),
            escape(_("Do not share this code outside the approved refund workflow.")),
            escape(company_name),
            escape(company_address or _("Address not specified")),
            escape(company_phone or _("Phone not specified")),
            escape(company_email or _("Email not specified")),
        )

    def action_request_myfatoorah_refund_otp(self):
        self.ensure_one()
        if not self.is_myfatoorah_refund:
            raise ValidationError(_("OTP approval is only available for MyFatoorah refunds."))

        self.transaction_id._check_myfatoorah_refund_access()
        recipients = self.transaction_id._get_myfatoorah_refund_otp_recipient_emails()
        otp_code = ''.join(secrets.choice('0123456789') for _ in range(6))
        validity_minutes = max(self.transaction_id.provider_id.myfatoorah_refund_otp_validity_minutes or 10, 1)
        expires_at = fields.Datetime.now() + timedelta(minutes=validity_minutes)
        sent_to = ', '.join(user.name for user, _email in recipients)
        self.write({
            'myfatoorah_otp_code': otp_code,
            'myfatoorah_otp_expires_at': expires_at,
            'myfatoorah_otp_sent': True,
            'myfatoorah_otp_sent_to': sent_to,
            'myfatoorah_otp_input': False,
        })

        amount_text = format_amount(self.env, self.amount_to_refund, self.currency_id)
        requester_name = self.env.user.name
        transaction_ref = self.transaction_id.reference
        for user, email in recipients:
            mail_values = {
                'subject': _("MyFatoorah Refund OTP for %s", transaction_ref),
                'email_to': email,
                'body_html': self._build_myfatoorah_otp_email_html(
                    requester_name, transaction_ref, amount_text, otp_code, validity_minutes, user
                ),
            }
            self.env['mail.mail'].sudo().create(mail_values).send()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'payment.refund.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_refund(self):
        for wizard in self:
            if wizard.transaction_id.provider_code == 'myfatoorah':
                wizard.transaction_id._check_myfatoorah_refund_access()
                remaining_amount = wizard.transaction_id._get_myfatoorah_remaining_refundable_amount()
                if wizard.amount_to_refund > remaining_amount:
                    raise ValidationError(_(
                        "The requested refund amount exceeds the remaining refundable balance."
                    ))
                if wizard.myfatoorah_amount_deducted_from_supplier < 0:
                    raise ValidationError(_("Amount Deducted From Supplier cannot be negative."))
                if wizard.myfatoorah_amount_deducted_from_supplier > wizard.amount_to_refund:
                    raise ValidationError(_("Amount Deducted From Supplier cannot exceed the refund amount."))
                if wizard.myfatoorah_require_otp:
                    if not wizard.myfatoorah_otp_sent or not wizard.myfatoorah_otp_code:
                        raise ValidationError(_("Please request a refund OTP first."))
                    if not wizard.myfatoorah_otp_input:
                        raise ValidationError(_("Please enter the refund OTP."))
                    if fields.Datetime.now() > wizard.myfatoorah_otp_expires_at:
                        raise ValidationError(_("The refund OTP has expired. Please request a new OTP."))
                    if wizard.myfatoorah_otp_input.strip() != wizard.myfatoorah_otp_code:
                        raise ValidationError(_("The entered refund OTP is invalid."))
                if not wizard.myfatoorah_refund_comment:
                    wizard.myfatoorah_refund_comment = _("Refund for %s", wizard.payment_id.display_name)
                wizard.transaction_id.with_context(
                    myfatoorah_refund_comment=wizard.myfatoorah_refund_comment,
                    myfatoorah_refund_external_identifier=wizard.myfatoorah_refund_external_identifier,
                    myfatoorah_amount_deducted_from_supplier=wizard.myfatoorah_amount_deducted_from_supplier,
                    myfatoorah_refund_otp_verified=True,
                ).action_refund(amount_to_refund=wizard.amount_to_refund)
            else:
                super(PaymentRefundWizard, wizard).action_refund()
