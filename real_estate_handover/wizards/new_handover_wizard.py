# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HandoverWizard(models.TransientModel):
    _name = 'handover.wizard'
    _description = 'Handover Wizard'

    handover_type = fields.Selection([
        ('handover', 'Handover'),
        ('handover_phpp', 'Handover-PHPP')
    ], string="Select a Record Type", required=True, default='handover')

    # Create Handover From Sale order With pre-filled Values Through Wizard
    def next_action(self):
        sale_order = self.env['sale.order'].browse(self._context.get('active_id'))
        return {
            'name': 'Handover Process',
            'type': 'ir.actions.act_window',
            'res_model': 'handover.process',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_customer_name': sale_order.partner_id.id if sale_order.partner_id else False,
                'default_handover_type': 'Handover',
                'default_unit': sale_order.order_line[
                    0].product_template_id.id if sale_order.order_line else False,
                'default_ho_owner_name': sale_order.create_uid.name,
                'default_owner_profile': sale_order.create_uid.partner_id.function,
                'default_customer_email': sale_order.partner_id.email if sale_order.partner_id else '',
                'default_handover_name': sale_order.order_line[
                    0].product_template_id.sap_unit_number if sale_order.order_line else '',
                'default_sale_order_id': sale_order.id,
                'default_purchase_price': sale_order.order_line[0].selling_price,
                'default_property_name': sale_order.order_line[0].product_template_id.property_name.id if sale_order.order_line else False,
                'default_owner': self.env.user.id,
                'default_is_manual_created': False,
        }
        }