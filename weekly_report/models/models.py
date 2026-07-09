# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import datetime,timedelta,date
from odoo.exceptions import ValidationError, UserError
from jinja2 import Environment, BaseLoader




class res_user_ext(models.Model):
    _inherit = 'res.users'

    weekly_report = fields.Boolean(string="Weekly Report")


class weekly_report(models.Model):
    _name = 'weekly.form'
    _description = 'Weekly Report'
    _rec_name = 'employee_id'
    _order = "id desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    week = fields.Char(string="Week" , tracking=True)
    active = fields.Boolean(string="Active" , tracking=True,default=True)
    date_to = fields.Date(string="Date To",tracking=True,store=True)
    date_From = fields.Date(string="Date From",tracking=True,store=True)
    employee_id = fields.Many2one('res.users',string="Employee", tracking=True, copy=False, default=lambda self: self.env.user.id)
    employee_department = fields.Char(string="Department",tracking=True, compute='get_employee_department')
    task_detail = fields.Html(string="Task Detail")
    attachment_id = fields.Binary(string="Attachments", attachment=True, copy=False,store=True)
    week_field = fields.Char(string="Weeks" , compute='get_the_days', store=True)
    tree_link_id = fields.One2many('weekly.report.tree', 'tree_link')



    report_comments = fields.Text(string="Type Comment")
    report_replys = fields.Text(string="Type Reply")

    check_c = fields.Boolean(string="Check Comment's" , default=True)

    get_id = fields.Integer(string="Employee Own id" , compute="_get_id_employee" , required=False, readonly=True , default=0)
    get_ids = fields.Integer(string="Employee Own " , related='get_id')


    check_c_r = fields.Selection([

        ('one','comment'),
        ('two','reply'),
        ('three','none'),

        ], string="Status", default='three')






    state = fields.Selection([
        ('draft', 'Draft'),
        # ('confirm', 'Confirmed'),
        ('sub', 'Submitted'),
    ], string='State', default='draft',copy=False)


    # def action_notify(self):
    #     if not self.attachment_id:
    #         self.attachment_id.notify_success(message='Please enter The File')

    @api.onchange('date_to','date_From')
    def get_the_days(self):
        for x in self:
            # x.weekly_report = False
            # if x.employee_id:
            #     x.weekly_report = x.employee_id.weekly_report
            only_from = x.date_From.day
            only_to = x.date_to.day
            only_mont_to = x.date_to.month
            only_mont_year = x.date_to.year
            datetime_object = datetime.strptime(str(only_mont_to), "%m")
            month_name = datetime_object.strftime("%b")
            x.week_field =' {}-{} {} {}'.format(only_from,only_to,month_name,only_mont_year)


    @api.onchange('date_From','date_to')
    def get_days_difference(self):

        days_all = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        today_day = days_all[datetime.now().weekday()]



        if  today_day == days_all[0]:
            self.date_From = datetime.now() - timedelta(days=3)
            self.date_to = self.date_From + timedelta(days=6)

        if  today_day == days_all[1]:
            self.date_From = datetime.now() - timedelta(days=4)
            self.date_to = self.date_From + timedelta(days=6)


        if  today_day == days_all[2]:
            self.date_From = datetime.now() - timedelta(days=5)
            self.date_to = self.date_From + timedelta(days=6)

        if  today_day == days_all[3]:
            self.date_From = datetime.now() - timedelta(days=6)
            self.date_to = self.date_From + timedelta(days=6)


        if  today_day == days_all[4]:
            self.date_From = datetime.now()
            self.date_to = self.date_From + timedelta(days=6)

        if  today_day == days_all[5]:
            self.date_From = datetime.now() - timedelta(days=1)
            self.date_to = self.date_From + timedelta(days=6)

        if  today_day == days_all[6]:
            self.date_From = datetime.now() - timedelta(days=2)
            self.date_to = self.date_From + timedelta(days=6)



    def get_date_difference(self):
        delta = self.date_to - self.date_From
        for x in range(delta.days + 1):
            day =self.date_From + timedelta(days=x)
            record = self.env['weekly.form'].search([('date_From','<=',day),('date_to','>=',day),('employee_id','=',self.employee_id.id),('id','!=',self.id)])
            # if record:
            #     raise ValidationError("Record Alrready use!")









    @api.depends('employee_id')
    def _get_id_employee(self):
        print('getting idddd')
        print('getting idddd')
        print('getting idddd')


        for x in self:
            if x.employee_id:
                id_get = x.env['res.users'].search([('id','=',12)])

                if self.env.user.id == id_get.id:
                    x.get_id = id_get.id
                else:
                    x.get_id = 0
            else:
                pass



    def send_now_user_email(self,**opt):


        print('Sending Email From Weekly Report')
        print('Sending Email From Weekly Report')

        email_from = self.env['ir.mail_server'].sudo().search([],limit=1)

        for account in self:
            if account.employee_id:

                get_user_em = self.env['res.users'].search([('id','=',account.employee_id.id)])
                from_user_em = self.env['res.users'].search([('id','=',12)])


                if get_user_em.partner_id.email:
                    mail_obj = self.env['mail.mail']
                    send_to = "{0}".format(get_user_em.partner_id.email)
                    account_name = get_user_em.name
                    account_name2 = from_user_em.name

                    print("")



                    sale_person = []

                    sale_person.append(from_user_em.name)



                    comment = []

                    if self.report_comments:
                        comment.append(self.report_comments)
                    

                    form_design = """

                    <div style="width:100%";>

                    <div style="width:100%; text-align:center;">
                    </div> 
                    
                        <br/>
                    <h2 style="text-align:left;">
                        <b style="color: black;">Weekly Report Comment Notification</b>
                    </h2>
                       
                        <br/>
                         <span style="font-weight:bold;">From</span> :   
                         {%for person in sale_person%}
                            <span style="font-weight:bold;">{{person}}</span>
                        {%endfor%}
                        <br/>
                        <span style="font-weight:bold;">To</span> :   
                            <span style="font-weight:bold;">{{account_name}}</span>
                        <br/>
                        <br/>

                        <span style="font-weight:bold;">Comment</span> :   
                         {%for c in comment%}
                            <span style="font-weight:normal;">{{c}}</span>
                        {%endfor%}

                        <br/>
                        <br/>


                     

                        <br/>
                        <br/>

                        

                        <br/>
                        <br/>
                        <b>Regards:</b>
                        <br/>
                        Togather Tourism
                        <br/>

                        <br/>

                        <div class="custom_footer" style="width:100%;">

                        </div>
                        </div>
                            


                    """
                    
                    template = Environment(loader=BaseLoader).from_string(form_design)
                    template_vars = {"sale_person": sale_person,"account_name": account_name,"comment":comment,"account_name2":account_name2}
                    html_out = template.render(template_vars)
                    my_mail =  mail_obj.sudo().create({
                    'email_from': email_from.smtp_user,
                    'email_to': send_to,
                    'model': 'weekly.form',
                    'res_id':self.id,
                    'subject': "Weekly Report Comment Notification (From : " + str(account_name2)+")",
                    'body_html':
                    '''<span  style="font-size: 14px"><br/>
                      <br/>%s </span> 
                      <br/><br/>''' % (html_out)}).sudo().send()
    




    def get_comments_sattus(self, vals):

        if vals.get('report_comments') != '' and vals.get('report_comments') != False:

            self.check_c = False
            self.check_c_r = 'one'
            print('check 111')
            self.send_now_user_email()



    def get_replys_sattus(self, vals):
        if vals.get('report_replys') != '':
            self.check_c_r = 'two'
            print('check 222')



    def write(self, vals):
        new_rec = super(weekly_report, self).write(vals)



        print(self.employee_id)
        print(self.employee_id)
        print(self.employee_id)

        self.get_date_difference()


        if self.check_c != False:
            if 'report_comments' in vals:
                print(vals)
                self.get_comments_sattus(vals)


        elif self.check_c != True:
            if 'report_replys' in vals:
                print(vals)
                self.get_replys_sattus(vals)



        return new_rec




    @api.model
    def create(self, vals):
        new_rec = super(weekly_report, self).create(vals)

        new_rec.get_date_difference()


        

        if new_rec.check_c != False:
            if 'report_comments' in vals:
                print(vals)
                new_rec.get_comments_sattus(vals)

        elif new_rec.check_c != True:
            if 'report_replys' in vals:
                print(vals)
                new_rec.get_replys_sattus(vals)

        return new_rec



    # @api.onchange('attachment_id')
    # def attachment_error(self):
    #     res={}
    #     if not self.attachment_id:
    #         res['warning'] = {'title': _('Warning'), 'message':'Please Add the Attachments File'}
    #         return res
        
    @api.depends('employee_id')
    def get_employee_department(self):
        for rec in self:
            emp_rec = self.env['hr.employee'].search([('user_id','=',rec.employee_id.id)])
            rec.employee_department = emp_rec.department_id.name
            # rec.week = str(rec.date_From)[:2] + '-' + str(rec.date_to)[:2] +

    def button_draft(self):
        self.state = 'draft'
    # def button_confirm(self):
        # self.state='confirm'
        # if not self.attachment_id:
        #     notification = {
        #     'type': 'ir.actions.client',
        #     'tag':'display_notification',
        #     'params': {
        #         'title': ('No Attachments'),
        #         'message': 'No attachment is attach in this record!',
        #         'type':'danger',  #types: success,warning,danger,info
        #         'sticky': False,

        #         },
        #     }
            

        # return notification


    def button_verified(self):
        self.state = 'sub'

    def unlink(self): 
        for x in self: 
            if x.state == 'sub': 
                raise ValidationError('Cannot Delete Record') 
        rec = super(weekly_report,self).unlink()
        return rec

class weekly_report_tree(models.Model):
    _name = "weekly.report.tree"
    _description = 'Weekly Tree'

    tree_link = fields.Many2one('weekly.form')
    task_detail = fields.Html(string="Task Detail")














class res_com_custom_ext(models.Model):
    _inherit = 'res.company'

    custom_cr_number = fields.Char(string="CR Number")