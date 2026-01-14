# -- encoding: utf-8 --
##############################################################################
#
#    Cloud Science Labs
#    Copyright (C) 2012 (https://www.cloudsciencelabs.com/)
#
##############################################################################
from odoo import models, fields, api, _,  exceptions
from odoo.exceptions import ValidationError
from collections import defaultdict
from datetime import datetime, timedelta


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    _description = 'Crm Lead'

    property_type = fields.Selection(
        [
            ("residential", "Residential"),
            ("commercial", "Commercial"),
        ],
        string="Classification Type",
        help="The type of the property",
    )
    planned_budget = fields.Float(string="Initial Planned Budget")
    possession_date = fields.Date(string="Initial Possession Date")
    locality = fields.Char(string="Locality")
    property_ids = fields.One2many('property.quotation.line', 'crm_id')
    cus_state = fields.Selection([
        ('new', 'New'),
        ('open_not_contacted', 'Open - Not Contacted'),
        ('working_contacted', 'Working - Contacted'),
        ('nurturing', 'Nurturing'),
        ('closed_not_converted', 'Closed - Not Converted'),
        ('closed_converted', 'Converted'), ], string="State",
        default='new',
        tracking=True,
    )
    dob = fields.Date(string="Date of Birth")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string="Gender")
    nationality = fields.Many2one('res.country', string="Nationality")
    marital_status = fields.Selection(
        [('single', 'Single'), ('married', 'Married'), ('divorced', 'Divorced'), ('widowed', 'Widowed')],
        string="Marital Status")
    # erp_reservation_number = fields.Char(string="ERP Reservation Number", readonly=True)

    # Lead Status
    lead_source = fields.Many2one('crm.lead.source', string="Lead Source")
    lead_type = fields.Many2one('crm.lead.type', string="Lead Type")
    lead_priority = fields.Selection([('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], string="Lead Priority")

    # Preference
    budget_from = fields.Monetary(string="Budget From", currency_field="currency_id")
    budget_to = fields.Monetary(string="Budget To", currency_field="currency_id")
    property = fields.Many2one('property.property', string="Property")
    preferred_language = fields.Selection([('hindi', 'Hindi'), ('english', 'English'), ('other', 'Other'), ],string="Preferred Language")
    client_preferred_contact_time = fields.Datetime(string="Client Preferred Contact Time")

    # Note And Remark
    telesales_comment = fields.Text(string="Telesales Comment")
    description = fields.Text(string="Description")

    # Unit Details
    user_ids = fields.Many2many('res.users', string="Assigned Users")
    unit_id = fields.Many2one('product.template', string="Unit")
    unit_project_name = fields.Char(string="Unit Project Name")
    unit_status = fields.Char(string="Unit Status")
    unit_building = fields.Char(string="Unit Building")
    unit_address = fields.Char(string="Unit Address")
    unit_floor = fields.Char(string="Unit Floor")
    unit_model = fields.Char(string="Unit Model")
    unit_total_area = fields.Char(string="Unit Total Area(sqft.)")

    # Financial Information
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    unit_amount = fields.Monetary(string="Unit Amount", currency_field="currency_id")
    paid_amount_receipt = fields.Float(string="Paid Amount (Receipt)")
    vat_amount = fields.Float(string="Vat Amount", currency_field="currency_id")
    total_unit_price = fields.Float(string="Total Unit Price", compute="compute_total_unit_price",
                                    currency_field="currency_id", help="Unit Amount - (Unit Amount * Discount /100) + Total Offer")
    discount = fields.Float(string="Discount (%)")
    selling_price = fields.Float(string="Selling Price(Vat + Charges)", compute="compute_selling_price",
                                 currency_field="currency_id", help="Total Unit Price + Total Charges + Total Vat Amount")
    total_offer = fields.Float(string="Total Offer(Amount)", currency_field="currency_id")
    total_charges = fields.Float(string="Total Charges(Amount)", currency_field="currency_id")

    # Payment Information
    payment_plan = fields.Many2one('product.subscription.period', string="Payment Plan")
    paid_amount_installments = fields.Float(string="Paid Amount (Installments)")
    is_all_amount_paid = fields.Boolean(string="Is All Amount Paid", compute="_compute_installment_totals",)
    remaining_amount = fields.Monetary(string="Remaining Amount", compute="_compute_installment_totals",currency_field="currency_id")
    charges_due_remaining_amount = fields.Float(string="Charges Due (Remaining Amount)")
    is_first_installment_paid = fields.Boolean(string="Is First Installment Paid", compute="_compute_installment_totals")
    amount_due_installments = fields.Float(string="Amount Due (Installments)")
    is_all_charges_paid = fields.Boolean(string="Is All Charges Paid")
    total_amount_received_installments = fields.Monetary(string="Total Amount Received (Installments)", compute="_compute_installment_totals", currency_field="currency_id")

    # Approval Details
    send_msg_to_manager1 = fields.Boolean(string="Approval Requested", default=False)
    manager1_button = fields.Boolean(string="Requested From Senior Manager", default=False)
    senior_manager_button = fields.Boolean(string="Approved Request", default=False)

    # Installments Details
    installment_line_ids = fields.One2many('crm.lead.installment', 'crm_lead_id', string="Installments")
    payment_plan_readonly = fields.Boolean(compute="_compute_payment_plan_readonly", store='True')
    invoice_count = fields.Integer(string="Invoice Count", compute="_compute_invoice_count")
    unit_id_readonly = fields.Boolean(compute="_compute_payment_plan_readonly", store=False)

    def _prepare_customer_values(self, partner_name, is_company, parent_id=False):
        res = super()._prepare_customer_values(partner_name, is_company, parent_id)
        res.update({
            'birth_date': self.dob,
            'marital_status': self.marital_status,
            'gender': self.gender,
            'function': self.function,
            'language_preference': self.preferred_language,
        })
        return res

    # calculate Payment Information fields based on installment lines
    @api.depends('installment_line_ids.paid_amount', 'installment_line_ids.remaining_amount','installment_line_ids.is_paid')
    def _compute_installment_totals(self):
        for lead in self:
            installments = lead.installment_line_ids
            lead.remaining_amount = sum(installments.mapped('remaining_amount'))
            lead.total_amount_received_installments = sum(installments.mapped('paid_amount'))
            lead.is_first_installment_paid = installments[0].is_paid if installments else False
            lead.is_all_amount_paid = lead.remaining_amount == 0.0

    def write(self, vals):
        res = super(CrmLead, self).write(vals)
        if 'stage_id' in vals:
            reserved_stage = self.env.ref('real_estate_management.stage_lead5', raise_if_not_found=False)
            for lead in self:
                if lead.stage_id == reserved_stage and lead.unit_id:
                    lead.unit_id.status = 'assign'
        return res

    # Recalculate and regenerate installment lines when payment plan or pricing details change
    @api.onchange('payment_plan', 'selling_price')
    def _onchange_installment_details(self):
        self.installment_line_ids = False
        if self.payment_plan and self.selling_price > 0:
            num_installments = self.payment_plan.duration
            amount_per_installment = self.selling_price / num_installments if num_installments else 0

            installment_lines = []
            for i in range(num_installments):
                due_date = fields.Date.today()
                if self.payment_plan.unit == 'days':
                    due_date += timedelta(days=i)
                elif self.payment_plan.unit == 'weeks':
                    due_date += timedelta(weeks=i)
                elif self.payment_plan.unit == 'month':
                    due_date += timedelta(days=30 * i)
                elif self.payment_plan.unit == 'year':
                    due_date += timedelta(days=365 * i)

                installment_lines.append((0, 0, {
                    'installment_name': f"Installment {i + 1}",
                    "due_date": due_date,
                    'remaining_amount': amount_per_installment,
                }))
            self.installment_line_ids = installment_lines


    # Function checked Budget To Not be less Than Budget From
    @api.constrains('budget_from', 'budget_to')
    def _check_budget_range(self):
        for record in self:
            if record.budget_to and record.budget_from and record.budget_to < record.budget_from:
                raise ValidationError("Budget To must be greater than or equal to Budget From.")

    # Compute total invoices linked to this CRM Lead
    @api.depends('installment_line_ids.invoice_id')
    def _compute_invoice_count(self):
        for lead in self:
            lead.invoice_count = len(lead.installment_line_ids.mapped('invoice_id'))

    # Action to open all invoices related to this CRM Lead
    def action_view_invoices(self):
        self.ensure_one()
        invoices = self.installment_line_ids.mapped('invoice_id')
        return {
            'name': 'Invoices',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', invoices.ids)],
            'context': {'create': False},
        }

    # Once a draft invoice is created for the first time, make the Payment Plan and unit readonly permanently
    @api.depends('installment_line_ids.invoice_id')
    def _compute_payment_plan_readonly(self):
        for lead in self:
            has_draft_invoice = any(inv.state == 'draft' for inv in lead.installment_line_ids.mapped('invoice_id'))
            lead.payment_plan_readonly = has_draft_invoice
            lead.unit_id_readonly = has_draft_invoice


    allowed_transitions = {
        'new': ['open_not_contacted','working_contacted'],
        'open_not_contacted': ['working_contacted'],
        'working_contacted': ['nurturing'],
        'nurturing': ['closed_converted','closed_not_converted'],
        'closed_converted': ['closed_not_converted','new'],
        'closed_not_converted': ['new'],
    }
    # Ensure state transitions follow the defined sequential flow in allowed_transitions
    @api.onchange('cus_state')
    def _check_state_transition(self):
        for lead in self:
            if lead._origin.cus_state:
                previous_state = lead._origin.cus_state
                new_state = lead.cus_state

                if new_state not in self.allowed_transitions.get(previous_state, []):
                    raise ValidationError(
                        f"Invalid transition from '{previous_state}' to '{new_state}'. Follow the correct sequence.")

    # Generate a unique ERP Reservation Number using the predefined sequence
    # def action_erp_reservation_number(self):
    #     sequence_code = 'real.estate.reservation'
    #     self.erp_reservation_number = self.env['ir.sequence'].next_by_code(sequence_code)

    # Property Consultant Sends a notification message to Manager for Approval
    def action_send_msg_to_manager1(self):
        manager_group = self.env.ref('real_estate_management.group_real_estate_manager_1')
        managers = self.env['res.users'].search([('groups_id', 'in', [manager_group.id])])

        if managers:
            for manager in managers:
                self.message_post(
                    body="Property Consultant Has Requested Approval.",
                    partner_ids=[manager.partner_id.id]
                )
        self.send_msg_to_manager1 = True

    # Manager approved the request and a notification message is sent to the Senior Manager for further approval
    def action_manager(self):
        senior_manager_group = self.env.ref('real_estate_management.group_real_estate_manager_2')
        senior_managers = self.env['res.users'].search([('groups_id', 'in', senior_manager_group.id)])

        if senior_managers:
            for manager in senior_managers:
                self.message_post(
                    body="Manager has approved this lead. Senior Manager approval is needed.",
                    partner_ids=[manager.partner_id.id]
                )
        self.manager1_button = True

    # Senior Manager approves and updates the stage to "Reserved"
    def action_senior_manager(self):
        reserved_stage = self.env['crm.stage'].search([('name', '=', 'Reserved')], limit=1)
        if reserved_stage:
            self.stage_id = reserved_stage.id
            self.message_post(body="Senior Manager has approved. Stage changed to Reserved.")
        self.senior_manager_button = True

    # computes the total unit price
    @api.depends('unit_amount', 'discount')
    def compute_total_unit_price(self):
        for record in self:
            discount_amount = (record.unit_amount * record.discount) / 100
            record.total_unit_price = record.unit_amount - (discount_amount + record.total_offer)

    # Computes the selling price by adding total unit price, total charges, and VAT amount
    @api.depends('total_unit_price', 'total_charges')
    def compute_selling_price(self):
        for record in self:
            record.selling_price = record.total_unit_price + record.total_charges + record.vat_amount

    # Auto-fills unit-related fields when a unit is selected
    @api.onchange('unit_id')
    def _onchange_unit_id(self):
        if self.unit_id:
            self.unit_project_name = self.unit_id.property_name.project_id.name
            self.vat_amount = self.unit_id.vat_tax
            self.unit_status = self.unit_id.status
            self.unit_building = self.unit_id.property_name.name
            self.unit_address = self.unit_id.city
            self.unit_floor = self.unit_id.floor.name
            self.unit_model = self.unit_id.unit_type_id.name
            self.unit_total_area = self.unit_id.square_feet
            self.unit_amount = self.unit_id.unit_price
            self.payment_plan = self.unit_id.payment_plan
            self.total_charges = sum(self.unit_id.utility_ids.mapped('price'))

    def get_opportunity_customers(self):
        opportunities = self.env['crm.lead'].search([('type', '=', 'opportunity')])
        partner_ids = opportunities.mapped('partner_id').ids
        partners = self.env['res.partner'].search([('id', 'in', partner_ids)])
        return partners.read(['name', 'email', 'phone', 'company_name', 'image_128'])

    # def write(self, vals):
    #     """Override the write method to trigger state creation when state changes to won."""
    #     res = super(CrmLead, self).write(vals)
    #     # Check if the state is being changed to 'won'
    #     if 'stage_id' in vals:
    #         won_stage = self.env['crm.stage'].search([('is_won', '=', True)], limit=1)  # Use XML ID for the "Won" stage
    #         if self.stage_id.id == won_stage.id:  # If the lead is now in the 'Won' stage
    #             for prop in self.mapped('property_ids').mapped('assigned_unit'):
    #                 prop.status = 'booked'
    #     return res


class PropertyQuotation(models.Model):
    _name = 'property.quotation.line'

    property_id = fields.Many2one('property.property', string="Property")
    floor_id = fields.Many2one('property.floor', string="Floor")
    query = fields.Char(string="Query")
    crm_id = fields.Many2one('crm.lead')
    type = fields.Many2one('crm.lead')
    property_type = fields.Selection(
        [
            ("residential", "Residential"),
            ("commercial", "Commercial"),
        ],
        string="Classification Type",
        help="The type of the property",
        related='crm_id.property_type'
    )
    assigned_unit = fields.Many2one('product.template', domain="[('property_type', '=', 'property_type')]")

    # On change of assigned_unit, validate project state and auto-fill related fields
    @api.onchange('assigned_unit')
    def onchange_assigned_units(self):
        for record in self:
            if record.assigned_unit.property_name.project_id.state != 'confirm' and record.assigned_unit:
                raise ValidationError(_("Please confirm the related project to select the unit."))
            record.property_id = record.assigned_unit.property_name.id
            record.floor_id = record.assigned_unit.floor.id
            record.assigned_unit.status = 'assign'
