# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools.misc import format_date
from datetime import  timedelta
from odoo.tools import float_is_zero

class AccountPartnerLedger(models.AbstractModel):
    _inherit = "account.partner.ledger.report.handler"

    filter_account = True

    @api.model
    def _get_options_domain(self, options):
        domain = super(AccountPartnerLedger, self)._get_options_domain(options)
        if options.get('account') and options.get('account_ids'):
            domain += [
                ('account_id','in',options.get('account_ids') )
            ]

        return domain

    @api.model
    def _get_report_line_move_line(self, options, partner, aml, cumulated_init_balance, cumulated_balance):
        if 'account_code' in aml and 'account_name' in aml:
            aml['account_code'] = aml['account_code'] +' '+aml['account_name']
        res = super(AccountPartnerLedger, self)._get_report_line_move_line(options, partner, aml,
                                                                           cumulated_init_balance, cumulated_balance)
        # if res.get('columns'):
        #     if aml.get('id'):
        #         moveid = self.env['account.move.line'].browse(aml.get('id')).move_id
        #         ref = moveid.partner_ref if moveid.move_type != 'entry' else ''
        #     columns = res.get('columns')
        #     columns.insert(3, {'name': ref}, )
        #     res.update({'columns': columns})
        return res
