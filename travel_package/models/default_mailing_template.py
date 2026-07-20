#-*- coding:utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError, UserError



class MailingMailingExt(models.Model):
    _inherit='mailing.mailing'

    @api.onchange('email_template')
    def set_body_html(self):
        print ("check 1")
        rec = self.search([('id','=',8),('active','=',False)])
        if self.email_template:
            print ("check 2")
            self.body_arch = self.email_template.body_arch
            self.body_html = self.email_template.body_html
        else:
            print ("check 3")
            self.body_arch = rec.body_arch
            self.body_html = rec.body_html

    def write(self, vals):
        ret = super(MailingMailingExt, self).write(vals)
        if self.id == 8:
            raise ValidationError("Cant Update this record")
        return ret

    def unlink(self):
        ret = super(MailingMailingExt, self).unlink()
        if self.id == 8:
            raise ValidationError("Cant Delete this record")
        return ret

class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'
    _description = 'Email composition wizard'

    def send_mail(self):
        res = super(MailComposer_inherit_c, self).send_mail()
        current_user= self.env.user.name

        body = "Send Email Button For Sending Booking Email's Has Been Used By {0}".format(str(current_user))

        print(current_user)
        ActiveModel = self.env[self.model].search([('id','=',self.res_id)])
        print(ActiveModel)
        print(ActiveModel.id)


        for x in self:
            if x.model =="all.services":
                if x.res_id == ActiveModel.id:
                    print('posting')
                    if ActiveModel.transportation_return: 
                        ActiveModel.transportation_return.message_post(body=body,subject="Pressing Booking Button")
                    elif ActiveModel.hotel_return: 
                        ActiveModel.hotel_return.message_post(body=body,subject="Pressing Booking Button")

        return res


    def _prepare_mail_values_static(self):
        return super()._prepare_mail_values_static()
