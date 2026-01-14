# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # Creating Sale Order from CRM
    def action_sale_quotations_new(self):
        if not self.unit_id:
            raise UserError("Please fill in the unit details before creating a quotation.")
        res = super().action_sale_quotations_new()

        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'opportunity_id': self.id,
            'state': 'reserved',
            'recurrance_id': self.payment_plan.id,
            'order_line': [(0, 0, {
                'product_id': self.unit_id.product_variant_id.id,
                'name': self.unit_id.product_variant_id.name,
                'product_uom_qty': 1,
                'product_uom': self.unit_id.product_variant_id.uom_id.id,
                'price_unit': self.unit_amount,
                'discount': self.discount,
                'selling_price': self.selling_price,
            })]
        })

        res['res_id'] = sale_order.id
        return res


