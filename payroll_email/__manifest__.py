# -*- coding: utf-8 -*-
{
    'name': "payroll_email",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com
        
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.mountsol.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_payroll','project', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/demo.xml',
        'views/templates.xml',
        'views/views.xml',
        'views/header.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
