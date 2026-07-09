from odoo import _, api, fields, models, modules, tools
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression
from odoo.tools import groupby
from odoo.tools.misc import clean_context

class mail_message_ext(models.Model):
    _inherit ='mail.message'
    _description= 'Message EXT'

    def _generate_model_record_ids(msg_val, msg_ids):
        model_record_ids = {}
        for id in msg_ids:
            vals = msg_val.get(id, {})
            if vals.get('model') and vals.get('res_id'):
                model_record_ids.setdefault(vals['model'], set()).add(vals['res_id'])
        return model_record_ids

        if self.env.is_superuser():
            return
        # Non employees see only messages with a subtype (aka, not internal logs)
        if not self.env['res.users'].has_group('base.group_user'):
            self._cr.execute('''SELECT DISTINCT message.id, message.subtype_id, subtype.internal
                                FROM "%s" AS message
                                LEFT JOIN "mail_message_subtype" as subtype
                                ON message.subtype_id = subtype.id
                                WHERE message.message_type = %%s AND (message.subtype_id IS NULL OR subtype.internal IS TRUE) AND message.id = ANY (%%s)''' % (self._table), ('comment', self.ids,))
            if self._cr.fetchall():
                raise AccessError(
                    _('The requested operation cannot be completed due to security restrictions. Please contact your system administrator.\n\n(Document type: %s, Operation: %s)') % (self._description, operation)
                    + ' - ({} {}, {} {})'.format(_('Records:'), self.ids[:6], _('User:'), self._uid)
                )

        # Read mail_message.ids to have their values
        message_values = dict((message_id, {}) for message_id in self.ids)

        self.flush(['model', 'res_id', 'author_id', 'parent_id', 'moderation_status', 'message_type', 'partner_ids', 'channel_ids'])
        self.env['mail.notification'].flush(['mail_message_id', 'res_partner_id'])
        self.env['mail.channel'].flush(['channel_message_ids', 'moderator_ids'])
        self.env['mail.channel.partner'].flush(['channel_id', 'partner_id'])
        self.env['res.users'].flush(['moderation_channel_ids'])

        if operation == 'read':
            self._cr.execute("""
                SELECT DISTINCT m.id, m.model, m.res_id, m.author_id, m.parent_id,
                                COALESCE(partner_rel.res_partner_id, needaction_rel.res_partner_id),
                                channel_partner.channel_id as channel_id, m.moderation_status,
                                m.message_type as message_type
                FROM "%s" m
                LEFT JOIN "mail_message_res_partner_rel" partner_rel
                ON partner_rel.mail_message_id = m.id AND partner_rel.res_partner_id = %%(pid)s
                LEFT JOIN "mail_message_res_partner_needaction_rel" needaction_rel
                ON needaction_rel.mail_message_id = m.id AND needaction_rel.res_partner_id = %%(pid)s
                LEFT JOIN "mail_message_mail_channel_rel" channel_rel
                ON channel_rel.mail_message_id = m.id
                LEFT JOIN "mail_channel" channel
                ON channel.id = channel_rel.mail_channel_id
                LEFT JOIN "mail_channel_partner" channel_partner
                ON channel_partner.channel_id = channel.id AND channel_partner.partner_id = %%(pid)s
                WHERE m.id = ANY (%%(ids)s)""" % self._table, dict(pid=self.env.user.partner_id.id, ids=self.ids))
            for mid, rmod, rid, author_id, parent_id, partner_id, channel_id, moderation_status, message_type in self._cr.fetchall():
                message_values[mid] = {
                    'model': rmod,
                    'res_id': rid,
                    'author_id': author_id,
                    'parent_id': parent_id,
                    'moderation_status': moderation_status,
                    'moderator_id': False,
                    'notified': any((message_values[mid].get('notified'), partner_id, channel_id)),
                    'message_type': message_type,
                }
        elif operation == 'write':
            self._cr.execute("""
                SELECT DISTINCT m.id, m.model, m.res_id, m.author_id, m.parent_id, m.moderation_status,
                                COALESCE(partner_rel.res_partner_id, needaction_rel.res_partner_id),
                                channel_partner.channel_id as channel_id, channel_moderator_rel.res_users_id as moderator_id,
                                m.message_type as message_type
                FROM "%s" m
                LEFT JOIN "mail_message_res_partner_rel" partner_rel
                ON partner_rel.mail_message_id = m.id AND partner_rel.res_partner_id = %%(pid)s
                LEFT JOIN "mail_message_res_partner_needaction_rel" needaction_rel
                ON needaction_rel.mail_message_id = m.id AND needaction_rel.res_partner_id = %%(pid)s
                LEFT JOIN "mail_message_mail_channel_rel" channel_rel
                ON channel_rel.mail_message_id = m.id
                LEFT JOIN "mail_channel" channel
                ON channel.id = channel_rel.mail_channel_id
                LEFT JOIN "mail_channel_partner" channel_partner
                ON channel_partner.channel_id = channel.id AND channel_partner.partner_id = %%(pid)s
                LEFT JOIN "mail_channel" moderated_channel
                ON m.moderation_status = 'pending_moderation' AND m.res_id = moderated_channel.id
                LEFT JOIN "mail_channel_moderator_rel" channel_moderator_rel
                ON channel_moderator_rel.mail_channel_id = moderated_channel.id AND channel_moderator_rel.res_users_id = %%(uid)s
                WHERE m.id = ANY (%%(ids)s)""" % self._table, dict(pid=self.env.user.partner_id.id, uid=self.env.user.id, ids=self.ids))
            for mid, rmod, rid, author_id, parent_id, moderation_status, partner_id, channel_id, moderator_id, message_type in self._cr.fetchall():
                message_values[mid] = {
                    'model': rmod,
                    'res_id': rid,
                    'author_id': author_id,
                    'parent_id': parent_id,
                    'moderation_status': moderation_status,
                    'moderator_id': moderator_id,
                    'notified': any((message_values[mid].get('notified'), partner_id, channel_id)),
                    'message_type': message_type,
                }
        elif operation == 'create':
            self._cr.execute("""SELECT DISTINCT id, model, res_id, author_id, parent_id, moderation_status, message_type FROM "%s" WHERE id = ANY (%%s)""" % self._table, (self.ids,))
            for mid, rmod, rid, author_id, parent_id, moderation_status, message_type in self._cr.fetchall():
                message_values[mid] = {
                    'model': rmod,
                    'res_id': rid,
                    'author_id': author_id,
                    'parent_id': parent_id,
                    'moderation_status': moderation_status,
                    'moderator_id': False,
                    'message_type': message_type,
                }
        else:  # unlink
            self._cr.execute("""SELECT DISTINCT m.id, m.model, m.res_id, m.author_id, m.parent_id, m.moderation_status, channel_moderator_rel.res_users_id as moderator_id, m.message_type as message_type
                FROM "%s" m
                LEFT JOIN "mail_channel" moderated_channel
                ON m.moderation_status = 'pending_moderation' AND m.res_id = moderated_channel.id
                LEFT JOIN "mail_channel_moderator_rel" channel_moderator_rel
                ON channel_moderator_rel.mail_channel_id = moderated_channel.id AND channel_moderator_rel.res_users_id = (%%s)
                WHERE m.id = ANY (%%s)""" % self._table, (self.env.user.id, self.ids,))
            for mid, rmod, rid, author_id, parent_id, moderation_status, moderator_id, message_type in self._cr.fetchall():
                message_values[mid] = {
                    'model': rmod,
                    'res_id': rid,
                    'author_id': author_id,
                    'parent_id': parent_id,
                    'moderation_status': moderation_status,
                    'moderator_id': moderator_id,
                    'message_type': message_type,
                }

        # Author condition (READ, WRITE, CREATE (private))
        author_ids = []
        if operation == 'read':
            author_ids = [mid for mid, message in message_values.items()
                          if message.get('author_id') and message.get('author_id') == self.env.user.partner_id.id]
        elif operation == 'write':
            author_ids = [mid for mid, message in message_values.items()
                          if message.get('moderation_status') != 'pending_moderation' and message.get('author_id') == self.env.user.partner_id.id]
        elif operation == 'create':
            author_ids = [mid for mid, message in message_values.items()
                          if not self.is_thread_message(message)]

        # Moderator condition: allow to WRITE, UNLINK if moderator of a pending message
        moderator_ids = []
        if operation in ['write', 'unlink']:
            moderator_ids = [mid for mid, message in message_values.items() if message.get('moderator_id')]
        messages_to_check = self.ids
        messages_to_check = set(messages_to_check).difference(set(author_ids), set(moderator_ids))
        if not messages_to_check:
            return

        # Recipients condition, for read and write (partner_ids)
        # keep on top, usefull for systray notifications
        notified_ids = []
        model_record_ids = _generate_model_record_ids(message_values, messages_to_check)
        if operation in ['read', 'write']:
            notified_ids = [mid for mid, message in message_values.items() if message.get('notified')]

        messages_to_check = set(messages_to_check).difference(set(notified_ids))
        if not messages_to_check:
            return

        # CRUD: Access rights related to the document
        document_related_ids = []
        document_related_candidate_ids = [mid for mid, message in message_values.items()
                if (message.get('model') and message.get('res_id') and
                    message.get('message_type') != 'user_notification' and
                    (message.get('moderation_status') != 'pending_moderation' or operation not in ['write', 'unlink']))]
        model_record_ids = _generate_model_record_ids(message_values, document_related_candidate_ids)
        for model, doc_ids in model_record_ids.items():
            DocumentModel = self.env[model]
            if hasattr(DocumentModel, 'get_mail_message_access'):
                check_operation = DocumentModel.get_mail_message_access(doc_ids, operation)  ## why not giving model here?
            else:
                check_operation = self.env['mail.thread'].get_mail_message_access(doc_ids, operation, model_name=model)
            records = DocumentModel.browse(doc_ids)
            records.check_access_rights(check_operation)
            mids = records.browse(doc_ids)._filter_access_rules(check_operation)
            document_related_ids += [
                mid for mid, message in message_values.items()
                if (message.get('model') == model and
                    message.get('res_id') in mids.ids and
                    message.get('message_type') != 'user_notification' and
                    (message.get('moderation_status') != 'pending_moderation' or
                    operation not in ['write', 'unlink']))]

        messages_to_check = messages_to_check.difference(set(document_related_ids))

        if not messages_to_check:
            return

        # Parent condition, for create (check for received notifications for the created message parent)
        notified_ids = []
        if operation == 'create':
            # TDE: probably clean me
            parent_ids = [message.get('parent_id') for message in message_values.values()
                          if message.get('parent_id')]
            self._cr.execute("""SELECT DISTINCT m.id, partner_rel.res_partner_id, channel_partner.partner_id FROM "%s" m
                LEFT JOIN "mail_message_res_partner_rel" partner_rel
                ON partner_rel.mail_message_id = m.id AND partner_rel.res_partner_id = (%%s)
                LEFT JOIN "mail_message_mail_channel_rel" channel_rel
                ON channel_rel.mail_message_id = m.id
                LEFT JOIN "mail_channel" channel
                ON channel.id = channel_rel.mail_channel_id
                LEFT JOIN "mail_channel_partner" channel_partner
                ON channel_partner.channel_id = channel.id AND channel_partner.partner_id = (%%s)
                WHERE m.id = ANY (%%s)""" % self._table, (self.env.user.partner_id.id, self.env.user.partner_id.id, parent_ids,))
            not_parent_ids = [mid[0] for mid in self._cr.fetchall() if any([mid[1], mid[2]])]
            notified_ids += [mid for mid, message in message_values.items()
                             if message.get('parent_id') in not_parent_ids]

        messages_to_check = messages_to_check.difference(set(notified_ids))
        if not messages_to_check:
            return

        # Recipients condition for create (message_follower_ids)
        if operation == 'create':
            for doc_model, doc_ids in model_record_ids.items():
                followers = self.env['mail.followers'].sudo().search([
                    ('res_model', '=', doc_model),
                    ('res_id', 'in', list(doc_ids)),
                    ('partner_id', '=', self.env.user.partner_id.id),
                    ])
                fol_mids = [follower.res_id for follower in followers]
                notified_ids += [mid for mid, message in message_values.items()
                                 if message.get('model') == doc_model and
                                 message.get('res_id') in fol_mids and
                                 message.get('message_type') != 'user_notification'
                                 ]

        messages_to_check = messages_to_check.difference(set(notified_ids))
        if not messages_to_check:
            return

        if not self.browse(messages_to_check).exists():
            return
        if not self.env.user.has_group('reservation_link.email_for_security_custom'):
            raise AccessError(
                _('The requested operation cannot be completed due to security restrictions. Please contact your system administrator.\n\n(Document type: %s, Operation: %s)') % (self._description, operation)
                + ' - ({} {}, {} {})'.format(_('Records:'), list(messages_to_check)[:6], _('User:'), self._uid)
            )