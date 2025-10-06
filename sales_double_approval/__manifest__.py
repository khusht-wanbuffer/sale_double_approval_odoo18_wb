# -- coding: utf-8 --
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Wan Buffer Solution (<https://wanbuffer.com/>).
#
#    For Module Support : info@wanbuffer.com  or Call : +91 9638442270
#
##############################################################################

{
    'name': 'Sales Order Double Approval',
    'version': '18.0.0.0',
    'category': 'Sales',
    "license": "OPL-1",
    'author': 'Wan Buffer Services',
    'website': 'https://wanbuffer.com',
    'summary': """This module helps to set two separate approvals process for a
     sale order to ensure accuracy and compliance.""",
    'description': """This module enables a process where a sale order must be
     reviewed and approved by two separate individuals or departments before it
     is finalized. This is implemented to ensure accuracy, compliance, and 
     reduce the risk of errors and fraud in sales transactions.
     Contact Us:
            • Support: support@wanbuffer.com
            • Sales: sales@wanbuffer.com
            • Phone: +91 96384 42270
    """,
    'depends': ['base', 'sale_management'],
    'data': [
        'data/mail_activity.xml',
        'data/email_template.xml',
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
        'views/approval_menu.xml',
        'views/sale_order_views.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,   
}

