# -*- coding: utf-8 -*-
{
    'name': "Real Estate | DLP Process",
    'version': '18.0.1.0',
    'sequence': -1,
    'summary': """
        Implements a DLP process with issue tracking and activity scheduling
    """,
    'description': """ 
        Module to manage post-sales customer care under the DLP (Defect Liability Period) 
        process. It allows users to track issues, assign responsible users, 
        schedule follow-up activities, and collect customer feedback.
    """,
    'author': 'Cloud Science Labs',
    'maintainer': 'Cloud Science Labs',
    'website': 'https://www.cloudsciencelabs.com/',
    'license': 'LGPL-3',
    'depends': ['helpdesk','appointment'],
    'data': ['security/ir.model.access.csv',
             'data/dlp_sequence_number.xml',
             'data/cron.xml',
             'data/mail_service_appointment.xml',
             'data/mail_under_scope.xml',
             'wizards/after_rectification.xml',
             'wizards/customer_availability.xml',
             'wizards/schedule_appointment.xml',
             'wizards/under_scope.xml',
             'wizards/customer_feedback.xml',
             'wizards/buttons.xml',
             'report/case_report.xml',
             'data/mail.xml',
             'views/dlp_menu.xml',
             'views/incident_description.xml',
             'views/problem_code.xml',
             'views/category.xml',
             'views/dlp.xml',
             'views/dlp_case.xml',
             'views/service_appointment.xml',
             'views/property_customer.xml',
             'views/service_document_report.xml',
             ],
    'assets': {
        'web.assets_backend': [
            'dlp_process/static/src/css/style.css',
            'dlp_process/static/src/js/dashboard.js',
            'dlp_process/static/src/xml/dashboard.xml',
            'dlp_process/static/src/scss/dlp_dashboard.scss'
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    "currency": "USD",
    "price": "1500.0",
}
