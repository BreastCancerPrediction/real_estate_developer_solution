# -- encoding: utf-8 --
##############################################################################
#
#    Cloud Science Labs
#    Copyright (C) 2024 (https://www.cloudsciencelabs.com/)
#
##############################################################################
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date

class CrmLeadInstallment(models.Model):
    _name = 'crm.lead.installment'
    _description = 'CRM Lead Installment'

    crm_lead_id = fields.Many2one('crm.lead', string="Lead", required=True)
    installment_name = fields.Char(string='Name')
    due_date = fields.Date(string='Due Date')
    remaining_amount = fields.Float(string='Remaining Amount')
    paid_amount = fields.Float(string='Paid Amount')
    is_paid = fields.Boolean(string="Is Paid")
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True, ondelete='set null')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    payment_ids_applied = fields.Many2many('account.payment', string="Applied Payments", readonly=True)

    """ Generate a draft invoice only when an installment's due date arrives """
    def _generate_installment_invoices(self):
        AccountMove = self.env['account.move']
        ProductProduct = self.env['product.product']

        default_product = ProductProduct.search([], limit=1)
        if not default_product:
            return

        default_income_account = default_product.categ_id.property_account_income_categ_id or \
                                 self.env['account.account'].search([('internal_type', '=', 'income')], limit=1)

        due_installments = self.search([
            ('is_paid', '=', False),
            ('invoice_id', '=', False),
            ('due_date', '<=', date.today())
        ])

        for installment in due_installments:
            if not installment.crm_lead_id or not installment.crm_lead_id.unit_id:
                continue

            product_name = f"{installment.crm_lead_id.unit_id.name} {installment.installment_name}"
            product = ProductProduct.search([('name', '=', installment.crm_lead_id.unit_id.name)], limit=1)

            invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': installment.crm_lead_id.partner_id.id,
                'invoice_date': fields.Date.today(),
                'invoice_date_due': installment.due_date,
                'installment_id': installment.id,
                'invoice_line_ids': [(0, 0, {
                    'name': product_name,
                    'quantity': 1,
                    'price_unit': installment.remaining_amount,
                    'account_id': default_income_account.id,
                    'product_id': product.id,
                })]
            }

            invoice = AccountMove.create(invoice_vals)
            installment.invoice_id = invoice.id
        return True

    """Cron job to update installment payment status in crm lead based on invoices"""
    @api.model
    def cron_check_installments(self):
        invoices = self.env['account.move'].search([
            ('state', '=', 'posted'),
            ('installment_id', '!=', False)
        ])

        for invoice in invoices:
            installment = invoice.installment_id
            if not installment:
                continue

            reconciled_payments = invoice._get_reconciled_payments()
            new_payments = reconciled_payments - installment.payment_ids_applied

            paid_total = sum(new_payments.mapped('amount'))

            if paid_total:
                installment.paid_amount += paid_total
                installment.remaining_amount -= paid_total
                installment.payment_ids_applied |= new_payments

                if installment.remaining_amount <= 0:
                    installment.remaining_amount = 0.0
                    installment.is_paid = True
