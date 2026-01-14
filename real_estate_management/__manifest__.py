# -*- coding: utf-8 -*-
################################################################################
#
#    Cloud Science Labs
#    Copyright (C) 2024 (https://www.cloudsciencelabs.com/)
#
################################################################################
{
    'name': "Real Estate | Property Management System",
    'version': '18.0.1.0',
    'sequence': 1,
    'summary': """
       Enhanced real estate management with a property status dashboard (list/Kanban views), brochure generation, automated commission tracking, geographic mapping, installment management, automated invoicing, CRM integration, and document attachment support.
    """,
    'description': """
        Real Estate Management System
    """,
    'author': 'Cloud Science Labs',
    'maintainer': 'Cloud Science Labs',
    'price': '1000.0',
    'currency': 'USD',
    'website': 'https://www.cloudsciencelabs.com/',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'sale_management', 'website', 'website_crm',
                'base_geolocalize', 'web', 'sale', 'board', 'project', 'crm', 'sttl_sale_subscription'],
    'data': [
        'security/user_groups.xml',
        'security/property_security.xml',
        'security/real_estate_group.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/crm_opportunity_stage.xml',
        'data/real_estate_management_data.xml',
        'data/ir_cron_data.xml',
        'data/website_contact_us.xml',
        'data/change_category.xml',
        'views/unit_enquiry_mail.xml',
        'views/property_property_views.xml',
        'views/property_facility_views.xml',
        'views/property_tag_views.xml',
        'views/property_search_pannel_views.xml',
        'views/property_templates.xml',
        'views/property_commision_views.xml',
        'views/property_sale_views.xml',
        'views/property_rental_views.xml',
        'views/res_partner_views.xml',
        'views/rental_bill_views.xml',
        'views/property_auction_views.xml',
        'views/sales_dashboard.xml',
        'views/product_template_views.xml',
        'views/crm_lead_views.xml',
        'views/project_views.xml',
        'views/crm_lead_source.xml',
        'views/crm_lead_type.xml',
        'views/project_template.xml',
        'reports/property_sale_report.xml',
        'reports/property_project_report.xml',
        'reports/product_template_report.xml',
        'reports/property_report.xml',
        'wizards/property_sale_report_views.xml',
        'wizards/update_payment_plan.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'real_estate_management/static/src/js/property_website.js',
            'real_estate_management/static/src/js/property_item.js',
            'real_estate_management/static/src/js/form_validation.js',
            'real_estate_management/static/src/css/custom.css',
        ],
        'web.assets_backend': [
            'real_estate_management/static/src/components/**/*.js',
            'real_estate_management/static/src/components/**/*.xml',
            'real_estate_management/static/src/components/**/*.scss',
            'real_estate_management/static/src/components/**/*.css',
        ],
    },
    'demo': [
    ],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [
    ],
}
