# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sales Order'

    handovers = fields.One2many('handover.process', 'sale_order_id', string="Handovers", compute='compute_handover_records', readonly=False)
    state = fields.Selection(selection=[
        ('draft', 'New'),
        ('reserved', 'Reserved'),
        ('sale', 'Booked'),
        ('validation_in_progress', 'Validation In Progress'),
        ('approve_pending', 'Approve Pending'),
        ('sold', 'Sold'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('pi_paid', 'PI Paid'),
    ], string="Status", default='draft')
    account = fields.Char(string='Account')
    owner_share_percentage = fields.Integer(string='Owner Share Percentage(%)')
    unit = fields.Char(string='Unit')
    opportunity = fields.Char(string='Opportunity')
    booking_date = fields.Date(string='Booking Date')
    sold_date = fields.Date(string='Sold Date')
    sales_approved_date = fields.Date(string='Sales Approved Date')
    approve_pending_date = fields.Date(string='Approve Pending Date')
    contact_issued_date = fields.Date(string='Contact Issued Date')
    contact_final_delivery_date = fields.Date(string='Contact Final Delivery Date')
    sales_manager = fields.Char(string='Sales Manager')
    sales_admin_user = fields.Char(string='Sales Admin User')
    # selling_price = fields.Char(string='Selling Price')
    sap_update_flag = fields.Boolean(string=' SAP Update Flag')
    amount_payable = fields.Float(string='Amount Payable')
    reservation_amount = fields.Float(string='Reservation Amount')
    net_amount_in_words = fields.Char(string='Net Amount In Words')
    customer_signed_sap_date = fields.Date(string='Customer Signed SAP Date')
    sub_status = fields.Char(string='Sub Status')
    sales_pending_rejection_reason = fields.Char(string='Sales Pending/Rejection Reason')
    sub_status_remark = fields.Char(string='Sub Status Remark')
    sm_manager = fields.Char(string='SM Manager')
    passport_attached = fields.Binary(string='Passport Attached')
    company_code = fields.Char(string='Company Code')
    emirates_id_attached = fields.Binary(string='Emirates Id Attached')
    send_to_sap = fields.Boolean(string='Send To SAP')
    sap_contact_unique_number = fields.Char(string='SAP Contact Unique Number')
    adm_dld_pre_registered = fields.Char(string='ADM/DLD Pre Registered')
    show_validation = fields.Boolean(string='Show Validation')
    addc = fields.Char(string='ADDC')
    pname_broker_under = fields.Char(string='PName Broker Under')
    addc_comments = fields.Char(string='ADDC Comments')
    handover_count = fields.Integer(string="Handover Count", compute='compute_handover_count')
    custom_untaxed_total = fields.Monetary(string="Untaxed Total", store=True, compute='_compute_custom_totals',
                                           currency_field='currency_id')
    custom_tax_amount = fields.Monetary(string="Taxes", store=True, compute='_compute_custom_totals',
                                        currency_field='currency_id')
    custom_grand_total = fields.Monetary(string="Total", store=True, compute='_compute_custom_totals',
                                         currency_field='currency_id')

    # Computes totals for the order: untaxed total, tax amount, and grand total
    @api.depends('order_line.selling_price', 'order_line.price_total', 'currency_id', 'company_id')
    def _compute_custom_totals(self):
        for order in self:
            untaxed = sum(line.price_unit for line in order.order_line if not line.display_type)
            tax = sum(line.selling_price - line.price_unit for line in order.order_line if not line.display_type)
            order.custom_untaxed_total = untaxed
            order.custom_tax_amount = tax
            order.custom_grand_total = untaxed + tax

    # Computes and updates the count of handover records associated with the sale order
    def compute_handover_count(self):
        for order in self:
            order.handover_count = self.env['handover.process'].search_count([('sale_order_id', '=', order.id)])

    # Action to view associated handovers for the current sale order
    def action_view_handovers(self):
        return {
            'name': _('Handovers'),
            'type': 'ir.actions.act_window',
            'res_model': 'handover.process',
            'view_mode': 'list,form',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {'default_sale_order_id': self.id},
        }

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            # Update CRM Opportunity stage to "Booked"
            if order.opportunity_id:
                booked_stage = self.env['crm.stage'].search([('name', '=', 'Booked')], limit=1)
                if booked_stage:
                    order.opportunity_id.stage_id = booked_stage

            # Update product template status to "booked"
            for line in order.order_line:
                product_template = line.product_id.product_tmpl_id
                product_template.status = 'booked'

            # Validate deliveries after confirming orders
            for picking in order.picking_ids:
                if picking.state == 'draft':
                    picking.action_confirm()
                if picking.state in ['confirmed', 'assigned']:
                    picking.action_assign()
                    if picking.state == 'assigned':
                        picking.button_validate()
        return res

    # Overriding the write method to update opportunity stage and product status
    def write(self, vals):
        res = super().write(vals)
        for order in self:
            # Set booking_date when state becomes 'sale'
            if vals.get('state') == 'sale' and not order.booking_date:
                order.write({'booking_date': fields.Date.today()})

            # Set approve_pending_date when state becomes 'approve_pending'
            if vals.get('state') == 'approve_pending' and not order.approve_pending_date:
                order.write({'approve_pending_date': fields.Date.today()})

            # Set sold_date and update opportunity & product status when state becomes 'sold'
            if vals.get('state') == 'sold':
                updates = {}
                if not order.sold_date:
                    updates['sold_date'] = fields.Date.today()
                if order.opportunity_id:
                    sold_stage = self.env['crm.stage'].search([('name', '=', 'Sold')], limit=1)
                    if sold_stage:
                        order.opportunity_id.stage_id = sold_stage
                for line in order.order_line:
                    product_template = line.product_id.product_tmpl_id
                    product_template.status = 'occupied'
                if updates:
                    order.write(updates)
            if vals.get('state') == 'sale':
                order._action_confirm()
                for picking in order.picking_ids:
                    if picking.state == 'draft':
                        picking.action_confirm()
                    if picking.state in ['confirmed', 'assigned']:
                        picking.action_assign()
                        if picking.state == 'assigned':
                            picking.button_validate()
        return res

    def compute_handover_records(self):
        for order in self:
            if order.id:
                handover_ids = self.env['handover.process'].search([('sale_order_id', '=', order.id)])
                order.handovers = handover_ids
            else:
                order.handovers = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Fill account with customer name
            if 'partner_id' in vals and vals['partner_id']:
                partner = self.env['res.partner'].browse(vals['partner_id'])
                vals['account'] = partner.name

            # Fill unit with product name from first order line
            if 'order_line' in vals and vals['order_line']:
                first_line = vals['order_line'][0]
                if first_line and first_line[2].get('product_id'):
                    product = self.env['product.product'].browse(first_line[2]['product_id'])
                    vals['unit'] = product.name

            # Set booking date if state is 'sale'
            if vals.get('state') == 'sale' and not vals.get('booking_date'):
                vals['booking_date'] = fields.Date.today()

        return super().create(vals_list)

    # Action to open the Handover Wizard and pass the current Sale Order ID
    def new_handover(self):
        return {
            'name': 'Handover Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'handover.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sales_order_id': self.id}
        }

    # Change state to 'sale' when click send by email button
    def action_quotation_send(self):
        res = super(SaleOrder, self).action_quotation_send()
        self.write({'state': 'sale'})
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    selling_price = fields.Float('Selling Price')

