from odoo import fields, api, models
from odoo.exceptions import ValidationError
from datetime import timedelta


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def new_work_order(self):
        self.ensure_one()
        crm_lead = self.env['crm.lead'].search([
            ('unit_id', '=', self.id),
            ('stage_id.name', '=', 'Sold'),
            ('partner_id', '!=', False)
        ], limit=1)

        sale_order = self.env['sale.order'].search([
            ('opportunity_id', '=', crm_lead.id),
            ('sold_date', '!=', False)
        ], limit=1)

        sold_date = sale_order.sold_date
        if not sold_date:
            raise ValidationError("Sold Date is missing. Cannot proceed with Work Order creation.")

        expiry_date = sale_order.sold_date + timedelta(days=365)
        if fields.Date.today() > expiry_date:
            raise ValidationError(
                f"Work Order creation is no longer allowed. The Sold Date was {sold_date}, and the Work Order is only valid within 1 year from this date.")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Work Order',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_unit_id': self.id,
                'default_account': crm_lead.partner_id.id if crm_lead else False,
                'default_contractor': self.property_name.project_id.contractor,
            },
        }