# -*- coding: utf-8 -*-
# from odoo import http


# class PayrollEmail(http.Controller):
#     @http.route('/payroll_email/payroll_email', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payroll_email/payroll_email/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('payroll_email.listing', {
#             'root': '/payroll_email/payroll_email',
#             'objects': http.request.env['payroll_email.payroll_email'].search([]),
#         })

#     @http.route('/payroll_email/payroll_email/objects/<model("payroll_email.payroll_email"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payroll_email.object', {
#             'object': obj
#         })
