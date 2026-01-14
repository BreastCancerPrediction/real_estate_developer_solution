from odoo import models, fields, api


class SaleSubscriptionPricingInherit(models.Model):
    _inherit = 'sale.subscription.pricing'

    installment_percentage = fields.Float(string="Installment Percentage", required=True, default=0.0,
                                          help="Define the percentage of the total price to be paid in installments.")