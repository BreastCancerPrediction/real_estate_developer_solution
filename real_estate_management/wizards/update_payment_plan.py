from odoo import fields, models


class UpdatePaymentPlan(models.TransientModel):
    _name = 'update.payment.plan'

    payment_plan_id = fields.Many2one('product.subscription.period', string="Payment Plan")

    # This method allow to change the payment plan for multiple product from list view
    def action_update(self):
        active_ids = self.env.context.get('active_ids')
        products = self.env['product.template'].browse(active_ids)
        products.write({'payment_plan': self.payment_plan_id.id})