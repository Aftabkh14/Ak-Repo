from odoo import models, fields, api, _
import base64
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


class AdvanceSalary(models.Model):
    _name = 'advance.salary.account'
    date = fields.Datetime(string="Date")
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=False,
                               )
    journal_request = fields.Boolean(default=False)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Employee")
    amount = fields.Integer(string='Amount')
    journal_state = fields.Selection(selection=[
            ('post', 'Posted'),
            ('mail', 'Mail'),
            ('requested', 'Requested'),
        ], string='Status',
        default='post')
    journal_entry_reference = fields.Many2one('account.move',string='Journal Reference')

    def action_delete(self):
        self.unlink()

    def action_create_journal(self):
        # try:
        setting = self.env['res.config.settings'].search([])[0]
        journal_entry = self.env['account.move'].create({
            'move_type': 'entry',
            'date': self.date,
            'journal_id':self.journal_id.id,
            'line_ids': [
                (0, 0, {
                    'name': 'line_debit',
                    'account_id': setting.coa_for_advance_salary_id.id,
                    'partner_id':self.partner_id.id,
                    'debit':self.amount,
                    'credit': 0.0

                }),
                (0, 0, {
                    'name': 'line_creadit',
                    'account_id': self.env['account.journal'].search([('type','=','bank')]).default_account_id.id,
                    'partner_id': self.partner_id.id,
                    'credit':self.amount,
                    'debit': 0.0,

                }),
            ],
        })

        journal_entry.action_post()
        self.journal_state = 'mail'
        print(self.journal_state)
        # self.journal_entry_reference = journal_entry.name
        # print(self.journal_entry_reference)
        self.journal_entry_reference = journal_entry.id
        # except:
        #     raise ValidationError(_('Kindly Add Advance Salary Journal in Setting'))

    def action_send_advance_salary_mail(self):
        template = self.env.ref('payroll_email.email_advance_salary_send')
        template.send_mail(self.id, force_send=True)
        self.journal_state = 'requested'
        self.journal_request = True
        print("sdsd")

    def action_send_advance_salary_mail_approved(self):
        template = self.env.ref('payroll_email.email_advance_salary_approved_send')
        template.send_mail(self.id, force_send=True)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_generate_payroll_report(self):
        data = {'unpaid':0,'working':0}
        if next((obj for obj in self.worked_days_line_ids  if obj.code == "LEAVE90"), None):
            data['unpaid'] = next((obj for obj in self.worked_days_line_ids  if obj.code == "LEAVE90"), None).number_of_days
        if next((obj for obj in self.worked_days_line_ids  if obj.code == "WORK100"), None):
            data['working'] = next((obj for obj in self.worked_days_line_ids  if obj.code == "WORK100"), None).number_of_days

        data['bank_account'] = self.employee_id.address_home_id.bank_ids.acc_number

        report = self.env.ref('payroll_email.action_report_payroll').with_context(data)

        pdf = self.env['ir.actions.report']._render_qweb_pdf(report.id, [self.ids[0]])

        attachment = self.env['ir.attachment'].create({
            'name': 'Payroll Report.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf[0]),
            'res_model': 'hr.payslip',
            'res_id': self.ids[0],
            'mimetype': 'application/x-pdf'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }

    def action_payslip_paid(self):
        res = super(HrPayslip,self).action_payslip_paid()
        template = self.env.ref('payroll_email.email_payroll_send_to_employee')
        data = {'unpaid':0,'working':0}
        if next((obj for obj in self.worked_days_line_ids  if obj.code == "LEAVE90"), None):
            data['unpaid'] = next((obj for obj in self.worked_days_line_ids  if obj.code == "LEAVE90"), None).number_of_days
        if next((obj for obj in self.worked_days_line_ids  if obj.code == "WORK100"), None):
            data['working'] = next((obj for obj in self.worked_days_line_ids  if obj.code == "WORK100"), None).number_of_days

        report = self.env.ref('payroll_email.action_report_payroll').with_context(data)
        pdf = self.env['ir.actions.report']._render_qweb_pdf(report.id, [self.ids[0]])

        attachment = self.env['ir.attachment'].create({
            'name': 'Payroll Report.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf[0]),
            'res_model': 'hr.payslip',
            'res_id': self.ids[0],
            'mimetype': 'application/x-pdf'
        })
        template.attachment_ids = [attachment.id]
        template.send_mail(self.id, force_send=True)


# ---------------------------------------------------------------------------------------------------------------------
# class ResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'
#     coa_for_advance_salary_id = fields.Many2one(
#         comodel_name='account.account',
#         string='Advance Salary Account',
#         readonly=False,
#         related='company_id.account_journal_suspense_account_id',
#         domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id), ('user_type_id.type', 'in', ('receivable', 'payable'))]" %         [self.env.ref('account.data_account_type_current_assets').id, self.env.ref('account.data_account_type_current_liabilities').id],
#         # [self.env.ref('account.data_account_type_current_assets').id, self.env.ref(
#         #     'account.data_account_type_current_liabilities').id]
#         help='Bank Transactions are posted immediately after import or synchronization. '
#              'Their counterparty is the bank suspense account.\n'
#              'Reconciliation replaces the latter by the definitive account(s).')
# -----------------------------------------------------------------------------------------------------------------------


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    coa_for_advance_salary_id = fields.Many2one(
        comodel_name='account.account',
        string='Advance Salary Account',
        readonly=False,
        related='company_id.account_journal_suspense_account_id',
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id), ('account_type', 'in', ('asset_receivable', 'liability_payable'))]" %[self.env.ref('account.account_payment_method_manual_in').id, self.env.ref('account.account_payment_method_manual_out').id],
        help='Bank Transactions are posted immediately after import or synchronization. '
             'Their counterparty is the bank suspense account.\n'
             'Reconciliation replaces the latter by the definitive account(s).')

























# -------------------------------------------------------------------------------------------------------------------------


#                        This commended and new code added below this code which use to create new stages
# class Projects(models.Model):
#     _inherit = "project.project"
#
#
#     def create_stages(self):
#         for ref in ['payroll_email.stage_0','payroll_email.stage_1','payroll_email.stage_2','payroll_email.stage_3','payroll_email.stage_4','payroll_email.stage_5','payroll_email.stage_6']:
#             self.env.ref(ref).project_ids = [(4, self.id, 0)]
#         sequence_list = ['BackLog','To Do','In Progress','Ready For Review','Code Review and Testing','Delivered','Cancelled']
#         for stage in self.type_ids:
#             stage.sequence = sequence_list.index(stage.name)
# ---------------------------------------------------------------------------------------------------------------------
#                                   New code for creating new stages....
# class Projects(models.Model):
#     _inherit = "project.project"
#
#     def create_stages(self):
#         stage_data = [('BackLog', 0), ('To Do', 1), ('In Progress', 2), ('Ready For Review', 3),
#                       ('Code Review and Testing', 4), ('Delivered', 5), ('Cancelled', 6)]
#         TaskType = self.env['project.task.type']
#         for name, sequence in stage_data:
#             stage = TaskType.search([('name', '=', name)], limit=1) or TaskType.create({'name': name, 'sequence': sequence})
#             self.type_ids = [(4, stage.id, 0)]
#         for stage in self.type_ids: stage.sequence = next((seq for name, seq in stage_data if name == stage.name), -1)





