from odoo import _, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_refund_wizard(self):
        self.ensure_one()
        tx = self.payment_transaction_id
        if tx and tx.provider_code == 'myfatoorah':
            tx._check_myfatoorah_refund_access()
        return super().action_refund_wizard()

    def _get_payment_refund_wizard_values(self):
        values = super()._get_payment_refund_wizard_values()
        tx = self.payment_transaction_id
        if tx and tx.provider_code == 'myfatoorah':
            refund_sequence = len(tx._get_myfatoorah_refund_child_transactions()) + 1
            values.update({
                'myfatoorah_refund_comment': _("Refund for %s", self.display_name),
                'myfatoorah_refund_external_identifier': "%s-refund-%s" % (tx.reference, refund_sequence),
            })
        return values
