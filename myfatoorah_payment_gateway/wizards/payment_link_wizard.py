from markupsafe import Markup, escape

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import email_normalize, format_amount


class PaymentLinkWizard(models.TransientModel):
    _inherit = 'payment.link.wizard'

    @staticmethod
    def _get_partner_mobile_number(partner):
        if not partner:
            return ''
        if 'mobile' in partner._fields and partner.mobile:
            return partner.mobile
        return partner.phone or ''

    invoice_name = fields.Char(
        string='Invoice',
        compute='_compute_invoice_details',
    )
    customer_name = fields.Char(
        string='Customer',
        compute='_compute_invoice_details',
    )
    customer_email_display = fields.Char(
        string='Customer Email',
        compute='_compute_invoice_details',
    )
    partner_mobile = fields.Char(
        string='Mobile',
        compute='_compute_invoice_details',
    )
    due_date = fields.Date(
        string='Due Date',
        compute='_compute_invoice_details',
    )
    invoice_description = fields.Char(
        string='Description',
        compute='_compute_invoice_details',
    )
    amount_due = fields.Monetary(
        string='Amount Due',
        currency_field='currency_id',
        compute='_compute_invoice_details',
    )

    @api.depends('partner_id', 'res_model', 'res_id', 'amount_max')
    def _compute_invoice_details(self):
        for wizard in self:
            move = wizard.env[wizard.res_model].browse(wizard.res_id) if wizard.res_model and wizard.res_id else False
            partner = wizard.partner_id
            wizard.invoice_name = ''
            wizard.customer_name = partner.name or ''
            wizard.customer_email_display = partner.email or ''
            wizard.partner_mobile = self._get_partner_mobile_number(partner)
            wizard.due_date = False
            wizard.invoice_description = ''
            wizard.amount_due = wizard.amount_max or 0.0
            if move and move._name == 'account.move':
                wizard.invoice_name = move.display_name or move.name or ''
                wizard.customer_name = move.partner_id.name or wizard.customer_name
                wizard.customer_email_display = move.partner_id.email or wizard.customer_email_display
                wizard.partner_mobile = self._get_partner_mobile_number(move.partner_id) or wizard.partner_mobile
                wizard.due_date = move.invoice_date_due
                wizard.invoice_description = move.payment_reference or move.ref or move.invoice_origin or move.display_name or ''

    @api.depends('amount', 'amount_max')
    def _compute_warning_message(self):
        super()._compute_warning_message()
        for wizard in self:
            if wizard.warning_message or wizard.res_model != 'account.move':
                continue
            if not wizard.partner_mobile:
                wizard.warning_message = _(
                    "MyFatoorah requires the customer to have a mobile number before generating a payment link."
                )

    @api.depends('amount', 'currency_id', 'partner_id', 'company_id', 'warning_message')
    def _compute_link(self):
        super()._compute_link()
        for wizard in self:
            if wizard.warning_message:
                wizard.link = False

    @api.constrains('amount', 'amount_max')
    def _check_amount_within_invoice_balance(self):
        for wizard in self:
            if wizard.amount_max > 0 and wizard.amount > wizard.amount_max:
                raise ValidationError(_(
                    "You cannot generate a payment link for more than the outstanding invoice amount."
                ))

    def _prepare_url(self, base_url, related_document):
        url = super()._prepare_url(base_url, related_document)
        if self.res_model != 'account.move':
            return url
        return url.replace('//my/', '/my/')

    def _build_payment_link_email_html(self, move):
        self.ensure_one()
        base_url = move.get_base_url()
        amount_text = format_amount(self.env, self.amount, self.currency_id)
        amount_due_text = format_amount(self.env, move.amount_residual, move.currency_id)
        invoice_name = move.display_name or move.name or _("Invoice")
        company = move.company_id or self.env.company
        company_name = company.name or _("Our Company")
        company_logo_url = f"{base_url}/web/image/res.company/{company.id}/logo" if company.id else ''
        company_phone = company.phone or company.partner_id.phone or ''
        company_email = company.email or company.partner_id.email or ''
        company_website = company.website or ''
        company_address = company.partner_id.contact_address or ''
        due_date = move.invoice_date_due and move.invoice_date_due.strftime('%Y-%m-%d') or ''
        description = move.payment_reference or move.ref or invoice_name
        customer_name = move.partner_id.name or _("Customer")
        customer_email = move.partner_id.email or ''
        customer_mobile = self._get_partner_mobile_number(move.partner_id)
        currency = move.currency_id
        line_rows = []
        for line in move.invoice_line_ids.filtered(lambda l: not l.display_type or l.display_type == 'product'):
            line_rows.append("""
              <tr>
                <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;vertical-align:top;">%s</td>
                <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;text-align:center;white-space:nowrap;">%s</td>
                <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;text-align:right;white-space:nowrap;">%s</td>
              </tr>
            """ % (
                escape(line.name or ''),
                escape(str(line.quantity or 0.0)),
                escape(format_amount(self.env, line.price_total, currency)),
            ))
        line_rows_html = Markup('').join(Markup(row) for row in line_rows) if line_rows else Markup("""
              <tr>
                <td colspan="3" style="padding:10px 12px;border-bottom:1px solid #e5e7eb;text-align:center;color:#6b7280;">%s</td>
              </tr>
        """) % escape(_("No invoice lines available."))

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
          <a href="%s" style="color:#0f766e;text-decoration:none;">%s</a>
        </div>
      </div>
      <div style="font-size:15px;line-height:1.7;margin-bottom:18px;">%s</div>
      <div style="border:1px solid #e5e7eb;border-radius:12px;padding:18px 16px;background:#f8fafc;">
        <div style="font-size:13px;color:#6b7280;margin-bottom:6px;">%s</div>
        <div style="font-size:22px;font-weight:700;color:#111827;">%s</div>
        <div style="margin-top:14px;font-size:14px;line-height:1.7;">
          <div><strong>%s</strong> %s</div>
          <div><strong>%s</strong> %s</div>
          <div><strong>%s</strong> %s</div>
          <div><strong>%s</strong> %s</div>
          <div><strong>%s</strong> %s</div>
          <div><strong>%s</strong> %s</div>
        </div>
      </div>
      <div style="margin-top:18px;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;">
        <table role="presentation" style="width:100%%;border-collapse:collapse;font-size:14px;">
          <thead>
            <tr style="background:#f8fafc;">
              <th style="padding:12px;text-align:left;border-bottom:1px solid #e5e7eb;">%s</th>
              <th style="padding:12px;text-align:center;border-bottom:1px solid #e5e7eb;">%s</th>
              <th style="padding:12px;text-align:right;border-bottom:1px solid #e5e7eb;">%s</th>
            </tr>
          </thead>
          <tbody>
            %s
          </tbody>
        </table>
      </div>
      <div style="margin:24px 0 20px;text-align:center;">
        <a href="%s" style="display:inline-block;background:#0f766e;color:#ffffff;text-decoration:none;font-weight:700;font-size:16px;padding:14px 26px;border-radius:10px;">%s</a>
      </div>
      <div style="font-size:13px;color:#6b7280;line-height:1.7;word-break:break-word;">
        %s<br/>
        <a href="%s" style="color:#0ea5e9;text-decoration:none;">%s</a>
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
            escape(_("Payment Request")),
            escape(company_name),
            escape(_("Company Information")),
            escape(company_address or _("Address not specified")),
            escape(company_phone or _("Phone not specified")),
            escape(company_email or _("Email not specified")),
            escape(company_website or base_url),
            escape(company_website or base_url),
            escape(_("Please use the secure payment link below to review the invoice and complete payment online.")),
            escape(_("Amount to Pay")),
            escape(amount_text),
            escape(_("Invoice:")),
            escape(invoice_name),
            escape(_("Customer:")),
            escape(customer_name),
            escape(_("Email:")),
            escape(customer_email or _("Not specified")),
            escape(_("Mobile:")),
            escape(customer_mobile or _("Not specified")),
            escape(_("Description:")),
            escape(description),
            escape(_("Due Date:")),
            escape(due_date or _("Not specified")),
            escape(_("Item")),
            escape(_("Qty")),
            escape(_("Amount")),
            line_rows_html,
            escape(self.link),
            escape(_("Review Invoice and Pay")),
            escape(_("Outstanding balance on invoice: %s. If the button does not open, use this link:", amount_due_text)),
            escape(self.link),
            escape(self.link),
            escape(company_name),
            escape(company_address or _("Address not specified")),
            escape(company_phone or _("Phone not specified")),
            escape(company_email or _("Email not specified")),
        )

    def action_send_payment_link_email(self):
        self.ensure_one()
        if self.warning_message:
            raise ValidationError(self.warning_message)
        if self.res_model != 'account.move':
            raise ValidationError(_("This action is only available for invoices."))
        if not self.partner_email:
            raise ValidationError(_("This customer has no email address."))
        normalized_email = email_normalize(self.partner_email)
        if not normalized_email:
            raise ValidationError(_("Please enter a valid customer email address."))

        move = self.env[self.res_model].browse(self.res_id)
        mail_values = {
            'subject': _("Payment Link for %s", move.display_name),
            'email_to': normalized_email,
            'body_html': self._build_payment_link_email_html(move),
        }
        mail = self.env['mail.mail'].sudo().create(mail_values)
        mail.send()
        move.message_post(
            body=_(
                "Payment link emailed to %(email)s for %(amount)s.",
                email=normalized_email,
                amount=format_amount(self.env, self.amount, self.currency_id),
            ),
            subtype_xmlid='mail.mt_note',
        )
        return {'type': 'ir.actions.act_window_close'}
