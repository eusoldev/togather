# -*- coding: utf-8 -*-

from odoo import models, fields, api


class mail_tracking(models.Model):
    _inherit = 'mail.mail'
    _description = 'Mail Tracking'


    def mail_tracking_ext(self):
        if self.model and self.res_id:
            body = ''
          
            if self.state =='sent':
                body = "Email Send Successfully."
            elif self.state =='recieved':
                body = "Email has been Recieved."
            else:
                if self.state=='exception':
                    if self.failure_reason:
                        body = self.failure_reason
                # else:
                #     body = "Email not sent because email is on " + str(dict(self._fields['state'].selection).get(self.state)) + " stage"

            self.mail_message_id.body =body


    @api.model
    def create(self, vals):
    
        new_rec = super(mail_tracking, self).create(vals)
        new_rec.mail_tracking_ext()

        return new_rec

    def write(self, vals):
        new_rec = super(mail_tracking, self).write(vals)
        for x in self:
            x.mail_tracking_ext()
            break
        return True

    