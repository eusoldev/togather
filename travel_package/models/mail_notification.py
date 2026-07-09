#-*- coding:utf-8 -*-
########################################################################################
########################################################################################
##                                                                                    ##
##    Odoo13                                                                          ##
##    Copyright (C) 2019 odoo13  (<http://ecube.pk>). All Rights Reserved             ##
##    contact us  at                                   for your erp needs.            ##
## Odoo is an all-in-one business software including CRM, e-commerce, accounting,MRP, ##
## Project management, and inventory. It helps you to improve the quality and         ##
## efficiency of your business.                                                       ##
########################################################################################
########################################################################################

from odoo import models, fields, api,_

from lxml import etree
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import datetime, timedelta, date

from dateutil.relativedelta import relativedelta

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import logging
import base64
from jinja2 import Environment, BaseLoader
import requests
from odoo.http import request

from datetime import timedelta
import logging
from hijri_converter import convert
from odoo.exceptions import ValidationError, UserError
_logger = logging.getLogger(__name__)


class Followers(models.Model):
    _inherit = ['mail.followers']

    def _get_recipient_data(self, records, message_type, subtype_id, pids=None):
        recipients_data = super()._get_recipient_data(records, message_type, subtype_id, pids=pids)
        if not (pids or records):
            return recipients_data

        if pids is None and records:
            records_pids = dict(
                (rec_id, partners.ids)
                for rec_id, partners in records._mail_get_partners().items()
            )
        elif pids and records:
            records_pids = dict((record.id, pids) for record in records)
        else:
            records_pids = {0: pids if pids else []}
        try:
            for rid, rdata in recipients_data.items():
                mail_pids = records_pids.get(rid) or []
                for pid, pdata in rdata.items():
                    if pid not in mail_pids and records and records[0]._name == 'all.services':
                        pdata['notif'] = False
        except:
            pass
        return recipients_data

# This class for Remove fllower in Email or send one email split multiple receipnts
class MailThreadEXT(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_compute_recipients(self, message, msg_vals):
        msg_sudo = message.sudo()
        pids = msg_vals.get('partner_ids', []) if msg_vals else msg_sudo.partner_ids.ids
        print(pids)
        print(pids)
        print(pids)
        print(pids)
        print(pids)
        cids = msg_vals.get('channel_ids', []) if msg_vals else msg_sudo.channel_ids.ids
        message_type = msg_vals.get('message_type') if msg_vals else msg_sudo.message_type
        subtype_id = msg_vals.get('subtype_id') if msg_vals else msg_sudo.subtype_id.id
        recipient_data = {
            'partners': [],
            'channels': [],
        }
        res = self.env['mail.followers']._get_recipient_data(self, message_type, subtype_id, pids, cids)
        if not res:
            return recipient_data
        author_id = msg_vals.get('author_id') or message.author_id.id
        for pid, cid, active, pshare, ctype, notif, groups in res:
            if pid and pid == author_id and not self.env.context.get('mail_notify_author'):  # do not notify the author of its own messages
                continue
            if pid:
                # This is custom condition in this function
                if pid in pids:
                    # End custom condition
                    if active is False:
                        continue
                    pdata = {'id': pid, 'active': active, 'share': pshare, 'groups': groups}
                    if notif == 'inbox':
                        recipient_data['partners'].append(dict(pdata, notif=notif, type='user'))
                    elif not pshare and notif:  # has an user and is not shared, is therefore user
                        recipient_data['partners'].append(dict(pdata, notif=notif, type='user'))
                    elif pshare and notif:  # has an user but is shared, is therefore portal
                        recipient_data['partners'].append(dict(pdata, notif=notif, type='portal'))
                    else:  # has no user, is therefore customer
                        recipient_data['partners'].append(dict(pdata, notif=notif if notif else 'email', type='customer'))
                    print("{+++++++++++++++}")
                    print(recipient_data['partners'])
                    print("{+++++++++++++++}")
            elif cid:
                recipient_data['channels'].append({'id': cid, 'notif': notif, 'type': ctype})

        # add partner ids in email channels
        email_cids = [r['id'] for r in recipient_data['channels'] if r['notif'] == 'email']
        if email_cids:
            email_from = msg_vals.get('email_from') or message.email_from
            exept_partner = [r['id'] for r in recipient_data['partners']]
            if author_id:
                exept_partner.append(author_id)
            new_pids = self.env['res.partner'].sudo().search([
                ('id', 'not in', exept_partner),
                ('channel_ids', 'in', email_cids),
                ('email', 'not in', [email_from]),
            ])
            for partner in new_pids:
                recipient_data['partners'].append({'id': partner.id, 'share': True, 'active': True, 'notif': 'email', 'type': 'channel_email', 'groups': []})
        return recipient_data

    def message_post_with_template(self, template_id, email_layout_xmlid=None, auto_commit=False, **kwargs):
        if not kwargs.get('composition_mode'):
            kwargs['composition_mode'] = 'comment' if len(self.ids) == 1 else 'mass_mail'
        if not kwargs.get('message_type'):
            kwargs['message_type'] = 'notification'
        res_id = kwargs.get('res_id', self.ids and self.ids[0] or 0)
        res_ids = kwargs.get('res_id') and [kwargs['res_id']] or self.ids
        composer = self.env['mail.compose.message'].with_context(
            active_id=res_id,
            active_ids=res_ids,
            active_model=kwargs.get('model', self._name),
            default_composition_mode=kwargs['composition_mode'],
            default_model=kwargs.get('model', self._name),
            default_res_id=res_id,
            default_template_id=template_id,
            custom_layout=email_layout_xmlid,
        ).create(kwargs)
        if template_id:
            update_values = composer.onchange_template_id(template_id, kwargs['composition_mode'], self._name, res_id)['value']
            composer.write(update_values)
        print(auto_commit)
        print(auto_commit)
        print(auto_commit)
        print("______________________________")
        if auto_commit:
            auto_commit = auto_commit
        else:
            auto_commit = False
        return composer.send_mail()

    def _message_auto_subscribe_followers(self, updated_values, default_subtype_ids):
        fnames = []
        field = self._fields.get('user_id')
        user_id = updated_values.get('user_id')
        if field and user_id and field.comodel_name == 'res.users' and (getattr(field, 'tracking', False) or getattr(field, 'tracking', False)):
            user = self.env['res.users'].sudo().browse(user_id)
            try:
                if user.active:
                    pass
                    # return [(user.partner_id.id, default_subtype_ids, 'mail.message_user_assigned' if user != self.env.user else False)]
            except:
                pass
        return []

class Mailingtemplate(models.Model):
    _inherit='mailing.mailing'
    
    email_template = fields.Many2one('custom.email', string='Email Template')