# -- encoding: utf-8 --
##############################################################################
#
#    Cloud Science Labs
#    Copyright (C) 2024 (https://www.cloudsciencelabs.com/)
#
##############################################################################
from odoo import fields, models


class AccountMove(models.Model):
    """A class that inherits the already existing model account move to add
    the related property sale and rental records"""
    _inherit = 'account.move'

    property_order_id = fields.Many2one('property.sale',
                                        string="Property Order ID",
                                        help='The corresponding property '
                                             'sale order')
    property_rental_id = fields.Many2one('property.rental',
                                         string='Property Rental ID',
                                         help='The corresponding property '
                                              'rental order')
    installment_id = fields.Many2one('crm.lead.installment', string="CRM Installment")
