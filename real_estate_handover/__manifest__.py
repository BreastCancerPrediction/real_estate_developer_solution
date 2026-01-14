# -*- coding: utf-8 -*-
{
    'name': "Real Estate CRM | Handover",
    'version': '18.0.1.0',
    'sequence': 4,
    'summary': """
        Manage property handovers efficiently with document tracking, notifications, and workflow automation.
    """,
    'description': """ 
        This module streamlines the real estate handover process by enabling document tracking, automated notifications, 
        and seamless workflow management. It ensures smooth communication between stakeholders and enhances efficiency 
        in property transitions.
    """,
    'author': 'Cloud Science Labs',
    'maintainer': 'Cloud Science Labs',
    'website': 'https://www.cloudsciencelabs.com/',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'sale', 'sale_crm', 'real_estate_management'],
    'data': ['security/handover_access.xml',
             'security/ir.model.access.csv',
             'data/owner_mail.xml',
             'data/document_name_data.xml',
             'views/menu.xml',
             'wizards/new_handover_wizard.xml',
             'reports/handover_report.xml',
             'views/handover.xml',
             'views/sale_order.xml',
             'views/sale_order_report.xml',
             'views/handover_documents.xml',
             'views/scheduled_activity.xml',
             ],
    'installable': True,
    'application': True,
    'auto_install': False,
    "currency": "USD",
    "price": "1500.0",
}
