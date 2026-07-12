from odoo import _, models
from odoo.exceptions import AccessError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_generate_myfatoorah_payment_link(self):
        self.ensure_one()
        if not self.env.user.has_group('myfatoorah_payment_gateway.group_myfatoorah_payment_link_manager'):
            raise AccessError(_("You are not allowed to generate MyFatoorah payment links."))
        if self.move_type != 'out_invoice':
            raise ValidationError(_("Payment links are only available for customer invoices."))
        if self.state != 'posted':
            raise ValidationError(_("The invoice must be posted before generating a payment link."))
        if self.amount_residual <= 0:
            raise ValidationError(_("There is no outstanding amount to pay on this invoice."))
        action = self.env['ir.actions.act_window']._for_xml_id(
            'account_payment.action_invoice_order_generate_link'
        )
        action['context'] = {
            'active_model': 'account.move',
            'active_id': self.id,
        }
        return action
