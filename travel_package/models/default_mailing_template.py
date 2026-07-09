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
        """Prepare values always valid, not rendered or dynamic whatever the
        composition mode and related records.

        :return dict: a dict of (field name, value) to be used to populate
          values for each res_id in '_prepare_mail_values';
        """
        self.ensure_one()
        email_mode = self.composition_mode == 'mass_mail'

        if email_mode:
            subtype_id = False
        elif self.subtype_id:
            subtype_id = self.subtype_id.id
        else:
            subtype_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_comment')

        values = {
            'author_id': self.author_id.id,
            'mail_activity_type_id': self.mail_activity_type_id.id,
            'mail_server_id': self.mail_server_id.id,
            'message_type': 'email_outgoing' if email_mode else self.message_type,
            'parent_id': self.parent_id.id,
            'record_name': False if email_mode else self.record_name,
            'reply_to_force_new': self.reply_to_force_new,
            'subtype_id': subtype_id,
        }
        # specific to mass mailing mode
        if email_mode:
            values.update(
                auto_delete=self.auto_delete,
                is_notification=self.auto_delete_keep_log,
                model=self.model,
            )
        # specific to post mode
        else:
            # Several custom layouts make use of the model description at rendering, e.g. in the
            # 'View <document>' button. Some models are used for different business concepts, such as
            # 'purchase.order' which is used for a RFQ and and PO. To avoid confusion, we must use a
            # different wording depending on the state of the object.
            # Therefore, we can set the description in the context from the beginning to avoid falling
            # back on the regular display_name retrieved in ``_notify_by_email_prepare_rendering_context()``.
            model_description = self.env.context.get('model_description')
            values.update(
                email_add_signature=self.email_add_signature,
                # email_layout_xmlid=self.email_layout_xmlid,
                force_send=self.force_send,
                mail_auto_delete=self.auto_delete,
                model_description=model_description,
                record_alias_domain_id=self.record_alias_domain_id.id,
                record_company_id=self.record_company_id.id,
            )
        return values