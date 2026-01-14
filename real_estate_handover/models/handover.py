# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, exceptions
from odoo.exceptions import ValidationError
from odoo.exceptions import AccessError, UserError


class Handover(models.Model):
    _name = 'handover.process'
    _description = 'Handover'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'handover_name'

    document_id = fields.One2many('documents.attachment', 'handover_id', string="Document")
    sale_order_id = fields.Many2one('sale.order', string="Sales Order")
    state = fields.Selection([
        ('created', 'Created'),
        ('qa_snagging', 'QA Snagging Completed'),
        ('qa_de_snagging', 'QA De-Snagging Completed'),
        ('home_orientation', 'Home Orientation Sent'),
        ('appointment', 'Appointment Booked with Customer'),
        ('pre_cho', 'Pre CHO Check Completed'),
        ('cho_snagging', 'CHO Snagging Completed'),
        ('cho_de_snagging', 'CHO De-Snagging Completed'),
        ('settlement', 'Settlement Follow up'),
        ('finance_verified', 'Finance Verified'),
        ('mortgage', 'Mortgage Release'),
        ('title_deed', 'Title Deed Registration Completed'),
        ('utilities', 'Utilities Transfer Completed'),
        ('kho_appointment', 'KHO Appointment Scheduled'),
        ('handover_completed', 'Handover Completed')
    ], string='Status', default='created', tracking=True)

    handover_name = fields.Char(string='Handover Name')
    handover_type = fields.Char(string='Handover Type')
    status = fields.Char(string='Status')
    customer_name = fields.Many2one('res.partner', string='Customer Name')
    customer_email = fields.Char(string='Customer Email')
    comments = fields.Char(string='Comments')
    unit = fields.Many2one('product.template', string='Unit')
    unit_ready = fields.Boolean(string='Unit Is Ready')
    property_name = fields.Many2one('property.property', string="Property")
    date_of_customer_contacted = fields.Date(string='Date of Customer Contacted')
    ho_owner_name = fields.Char(string='Ho Owner Name', compute="_compute_ho_owner_name", store=True)
    owner_profile = fields.Char(string='Owner Profile')
    purchase_price = fields.Float(string='Purchase Price')
    is_manual_created = fields.Boolean(string='Is Manual Created', default=True)

    # operation team page fields
    adm_registration_fee = fields.Float(string='ADM Registrations Fee')
    mortgage_fee_rate = fields.Float(string='Mortgage Fee Rate')
    plot_number = fields.Char(string='Plot Number')

    # GR team page fields
    mortgage_release_amount = fields.Float(string='Mortgage Release Amount')
    adm_plot_number = fields.Char(string='ADM Plot Number')

    # finance team page fields
    early_settlement = fields.Char(string='Early Settlement')
    collection_till_handover_amount = fields.Float(string='Collection Till Handover Amount')
    collection_till_handover = fields.Boolean(string='Collection Till Handover')
    collection_on_ho = fields.Boolean(string='Collection on H.O')
    collection_of_pdcs = fields.Boolean(string="Collection of PDC's")
    collection_on_ho_amount = fields.Float(string="Collection on H.O Amount")
    collection_of_pdcs_amount = fields.Float(string="Collection of PDC's Amount")
    title_deed_fee = fields.Float(string="Title Deed Fee")
    hassantuk_fees = fields.Float(string="Hassantuk Fees")
    service_change_collection = fields.Boolean(string="Service Change Collection")
    mortgage_fee = fields.Float(string='Mortgage Fee')
    total_collection_before_ho = fields.Float(string='Total Collection Before HO')
    service_change_collection_amount = fields.Float(string="Service Change Collection Amount")
    ho_installment_collection = fields.Float(string="HO Installment Collection")
    bounced_cheque_fees = fields.Float(string="Bounced Chqs Fees")
    post_ho_pcds_collection = fields.Float(string="Post HO PCD's Collection")
    late_payment_fees = fields.Float(string="Late Payment Fees")
    adm_registration_fee_paid_by = fields.Char(string='ADM Registrations Fee Paid By')
    admin_fees = fields.Char(string='Admin Fees')
    service_charge_clearance = fields.Char(string='Service Charge Clearance')
    mortgage_bank_name = fields.Char(string='Mortgage Bank Name')
    service_charges_confirmed = fields.Char(string='Service Charges Confirmed')
    mortgage_fee_rate_by = fields.Char(string='Mortgage Fee Rate By')

    # crm team page fields
    orientation_appointment_status = fields.Char(string='Orientation Appointment Status')
    customer_availability_for_cho = fields.Selection(
        selection=[('none', 'None'), ('customer_delegate_to_bloom', 'Customer Delegate To Bloom'),
                   ('customer_available', 'Customer Available'), ('customer_not_available', 'Customer Not Available')],
        string='Customer Availability For CHO')
    promise_to_pay_date = fields.Date(string='Promise To Pay Date')
    payment_type = fields.Selection(selection=[('cash', 'Cash'), ('mortgage', 'Mortgage'), ('phpp', 'PHPP')],
                                    string='Payment Type', default="")
    expected_receive_date_mortgage = fields.Date(string='Expected Receive Date Mortgage')
    home_orientation_invitation_date = fields.Date(string='Home Orientation Invitation Date')
    owner_rep_name = fields.Char(string='Owner Rep. Name')
    bank_name = fields.Selection(selection=[('sbi', 'SBI'), ('hdfc', 'HDFC'), ('icici', 'ICICI'), ('axis', 'Axis')],
                                 string='Bank Name')
    owner_rep_number = fields.Char(string='Owner Rep. Number')
    bank_rep_name = fields.Char(string='Bank Rep. Name')
    owner_rep_email = fields.Char(string='Owner Rep. Email')
    bank_rep_phone = fields.Char(string='Bank Rep. Phone')
    notice_of_completion_date = fields.Date(string='Notice Of Completion Date')
    bank_rep_email = fields.Char(string='Bank Rep. Email')
    settlement_follow_up_date = fields.Date(string='Settlement Follow Up Date')
    mortgage_status = fields.Selection(
        selection=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        string='Mortgage Status')

    # process checklist page fields
    bcc_announcement_sent = fields.Boolean(string='Bcc Announcement Sent')
    orientation_letter_sent = fields.Boolean(string='Orientation Letter Sent')
    is_pre_checklist_completed = fields.Boolean(string='Is Pre-Checklist Completed')
    is_appointment_booked = fields.Boolean(string='Is Appointment Booked')
    notice_of_completion_sent = fields.Boolean(string='Notice Of Completion Sent', store=True)
    payment_settled = fields.Boolean(string='Payment Settled')
    is_title_deed_registration = fields.Boolean(string='Is Title Deed Registration')

    # leasing details page fields
    lease_start_date = fields.Date(string='Lease Start Date')
    leasing_agent = fields.Char(string='Leasing Agent')
    lease_end_date = fields.Date(string='Lease End Date')
    lease_type = fields.Selection(selection=[('short_term', 'Short Term'), ('long_term', 'Long Term')],
                                  string='Lease Type')
    lease_amount = fields.Float(string='Lease Amount')

    # key handover checklist fields
    is_statement_of_amount_given = fields.Boolean(string='Is Statement of Amount Given?')
    is_title_deed_issued = fields.Boolean(string='Is Title Deed Issued?')
    is_property_keys_given = fields.Boolean(string='Is Property Keys Given?')
    handover_guidelines_brief = fields.Boolean(string='Handover Guidelines Brief')
    is_access_card_given = fields.Boolean(string='Is Access Card Given?')
    addc = fields.Boolean(string='ADDC')

    # Assignments page fields
    owner = fields.Many2one('res.users', string='Responsible')
    operation_team_assigned_user = fields.Char(string='Operation Team Assigned User')
    ho_agent = fields.Char(string='HO Agent')
    crm_team_assigned_user = fields.Char(string='CRM Team Assigned User')

    allowed_transitions = {
        'created': ['qa_snagging'],
        'qa_snagging': ['qa_de_snagging'],
        'qa_de_snagging': ['home_orientation'],
        'home_orientation': ['appointment'],
        'appointment': ['pre_cho'],
        'pre_cho': ['cho_snagging'],
        'cho_snagging': ['cho_de_snagging'],
        'cho_de_snagging': ['settlement'],
        'settlement': ['finance_verified'],
        'finance_verified': ['mortgage'],
        'mortgage': ['title_deed'],
        'title_deed': ['utilities'],
        'utilities': ['kho_appointment'],
        'kho_appointment': ['handover_completed'],
        'handover_completed': ['created'],
    }

    # Validate Handover State Transitions Based on Allowed Sequence
    @api.onchange('state')
    def _check_state_transition(self):
        for record in self:
            if record._origin.state:
                previous_state = record._origin.state
                new_state = record.state

                if new_state not in self.allowed_transitions.get(previous_state, []):
                    raise ValidationError(
                        f"Invalid transition from '{previous_state}' to '{new_state}'. Follow the correct sequence.")

    # @api.constrains('owner', 'state')
    # def _check_required_fields_for_finance_group(self):
    #     required_fields = [
    #         'adm_registration_fee', 'mortgage_fee_rate', 'plot_number',
    #         'mortgage_release_amount', 'adm_plot_number', 'early_settlement',
    #         'collection_till_handover_amount', 'collection_till_handover', 'collection_on_ho',
    #         'collection_of_pdcs', 'collection_on_ho_amount', 'collection_of_pdcs_amount',
    #         'title_deed_fee', 'hassantuk_fees', 'service_change_collection', 'mortgage_fee',
    #         'total_collection_before_ho', 'service_change_collection_amount',
    #         'ho_installment_collection', 'bounced_cheque_fees', 'post_ho_pcds_collection',
    #         'late_payment_fees', 'adm_registration_fee_paid_by', 'admin_fees',
    #         'service_charge_clearance', 'mortgage_bank_name', 'service_charges_confirmed',
    #         'mortgage_fee_rate_by', 'orientation_appointment_status',
    #         'promise_to_pay_date', 'expected_receive_date_mortgage', 'home_orientation_invitation_date',
    #         'owner_rep_name', 'bank_name', 'owner_rep_number', 'bank_rep_name',
    #         'owner_rep_email', 'bank_rep_phone', 'notice_of_completion_date',
    #         'bank_rep_email', 'settlement_follow_up_date', 'mortgage_status',
    #         'lease_start_date', 'leasing_agent', 'lease_end_date', 'lease_type',
    #         'lease_amount', 'is_statement_of_amount_given', 'is_title_deed_issued',
    #         'is_property_keys_given', 'handover_guidelines_brief', 'is_access_card_given', 'addc'
    #     ]
    #     finance_group = self.env.ref('real_estate_handover.finance_group')
    #     for record in self:
    #         if record.state == 'finance_verified' and record.owner and finance_group in record.owner.groups_id:
    #             missing_fields = [
    #                 field for field in required_fields
    #                 if not getattr(record, field)
    #             ]
    #             if missing_fields:
    #                 raise ValidationError(
    #                     _("The following fields are required before proceeding to 'Finance' state: %s") % ", ".join(
    #                         missing_fields)
    #                 )

    # Auto-populate all predefined handover documents lines in Handover form
    @api.model
    def default_get(self, fields):
        res = super(Handover, self).default_get(fields)
        documents = self.env['handover.documents'].search([])
        attachment_vals = [{
            'handover_document_id': doc.id
        } for doc in documents]
        res['document_id'] = [(0, 0, vals) for vals in attachment_vals]
        return res

    # Send NOC to customer only after BCC Announcement is sent
    def send_noc_to_customer(self):
        for record in self:
            if not record.bcc_announcement_sent:
                raise exceptions.ValidationError(
                    "Please send BCC Announcement first before sending the NOC to the customer.")
            record.write({'notice_of_completion_sent': True})
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'NOC sent successfully!',
                    'type': 'rainbow_man'
                }
            }

    # Override the write method to handle conditional validations, state transitions, ownership reassignments and document checks
    def write(self, vals):
        # Validate that the unit is marked as ready before allowing transition to 'home_orientation' state.
        if 'state' in vals and vals['state'] == 'home_orientation':
            for record in self:
                if not record.unit_ready:
                    raise exceptions.ValidationError(
                        _("Unit must be ready before transitioning to 'Home Orientation'."))

        for record in self:
            old_owner = record.owner
            res = super(Handover, record).write(vals)

            # Prevent state change if required reports are missing
            state_requirements = {
                'qa_snagging': 'QA Snagging Report',
                'qa_de_snagging': 'QA Desnagging Report',
                'cho_snagging': 'CHO Snagging Report',
                'cho_de_snagging': 'CHO DeSnagging Report',
                'finance_verified': 'SOA',
                'mortgage': 'Bank NOC',
                'title_deed': 'Title deed Report',
                'utilities': 'ADDC'
            }
            if vals.get('state') in state_requirements:
                required_report_name = state_requirements[vals['state']]
                state_display_name = dict(self._fields['state'].selection).get(vals['state'], vals['state'])
                report_docs = record.document_id.filtered(
                    lambda d: d.handover_document_id and d.handover_document_id.name == required_report_name
                )
                if not report_docs or any(not doc.file and not doc.image for doc in report_docs):
                    raise exceptions.UserError(
                        f"You cannot change the state to '{state_display_name}' without a {required_report_name} containing a file or an image."
                    )

            # assignment to handover operation team when transitioning to QA desnagging
            if vals.get('state') == 'qa_de_snagging':
                operation_team_users = self.env['res.users'].search([
                    ('groups_id', 'in', self.env.ref('real_estate_handover.group_handover_operation_team_queue').id)
                ])
                if operation_team_users:
                    user_handover_counts = {
                        user: self.env['handover.process'].search_count([('owner', '=', user.id)])
                        for user in operation_team_users
                    }
                    new_owner = min(user_handover_counts, key=user_handover_counts.get)
                    record.owner = new_owner

            # Assign the record to a user from the Government Team when transitioning to Mortgage Release
            if vals.get('state') == 'mortgage':
                govt_team_users = self.env['res.users'].search([
                    ('groups_id', 'in', self.env.ref('real_estate_handover.group_government_team').id)
                ])
                if govt_team_users:
                    new_owner = min(govt_team_users, key=lambda user: self.env['handover.process'].search_count(
                        [('owner', '=', user.id)]
                    ))
                    record.owner = new_owner

            # Assign the record to a user from the CRM Team when transitioning to Title deed
            if vals.get('state') == 'title_deed':
                crm_users = self.env['res.users'].search([
                    ('groups_id', 'in', self.env.ref('real_estate_handover.group_crm_user').id)
                ])
                if crm_users:
                    new_owner = min(crm_users, key=lambda user: self.env['handover.process'].search_count(
                        [('owner', '=', user.id)]
                    ))
                    record.owner = new_owner
                    record.is_title_deed_registration = True

            # Assign the record to a user from the CRM Team when transitioning to CHO desnagging
            if vals.get('state') == 'cho_de_snagging':
                crm_users = self.env['res.users'].search([
                    ('groups_id', 'in', self.env.ref('real_estate_handover.group_crm_user').id)
                ])
                if crm_users:
                    user_handover_counts = {
                        user: self.env['handover.process'].search_count([('owner', '=', user.id)])
                        for user in crm_users
                    }
                    new_owner = min(user_handover_counts, key=user_handover_counts.get)
                    record.owner = new_owner

            # Prevent state change to 'settlement' if Emirates ID and Passport and notice of completion is missing
            if vals.get('state') == 'settlement':
                required_docs = ['Emirates ID', 'Passport']
                for doc_name in required_docs:
                    doc = record.document_id.filtered(
                        lambda d: d.handover_document_id and d.handover_document_id.name == doc_name
                    )
                    if not doc or any(not d.file and not d.image for d in doc):
                        raise exceptions.ValidationError(
                            f"You cannot change the state to 'Settlement' without an {doc_name} containing a file or an image."
                        )
                if not record.notice_of_completion_sent:
                    raise exceptions.ValidationError("Please send NOC first before settlement.")
                if not record.payment_type:
                    raise exceptions.ValidationError("Payment Type cannot be empty when settling.")
                record.payment_settled = True
                finance_users = self.env['res.users'].search([
                    ('groups_id', 'in', self.env.ref('real_estate_handover.finance_group').id)
                ])

                # Assign the record to a user from the Finance Team when transitioning to Settlement
                if finance_users:
                    user_handover_counts = {
                        user: self.env['handover.process'].search_count([('owner', '=', user.id)])
                        for user in finance_users
                    }
                    new_owner = min(user_handover_counts, key=user_handover_counts.get)
                    record.owner = new_owner

            # Assign the record to a user from the Handover Operation Team when transitioning to Finance Verified
            if vals.get('state') == 'finance_verified':
                operation_team_users = self.env['res.users'].search([
                    ('groups_id', 'in', self.env.ref('real_estate_handover.group_handover_operation_team_queue').id)
                ])
                if operation_team_users:
                    new_owner = min(operation_team_users, key=lambda user: self.env['handover.process'].search_count(
                        [('owner', '=', user.id)]))
                    record.owner = new_owner

            if vals.get('state') == 'pre_cho':
                record.is_pre_checklist_completed = True

            # Log ownership changes and send email
            if 'owner' in vals and old_owner.id != vals['owner']:
                new_owner = self.env['res.users'].browse(vals['owner'])

                # Log message in chatter
                message = _("User %s now owns the record for %s.") % (new_owner.name, record.handover_name)
                record.message_post(body=message)

                # Send email notification
                template = self.env.ref('real_estate_handover.email_template_handover_to_owner')
                if template:
                    template.send_mail(record.id, force_send=True)

        return res

    # Display a notification when the 'owner' field is changed in the Handover form
    @api.onchange('owner')
    def _onchange_owner(self):
        if self.owner:
            return {
                'warning': {
                    'title': "Owner Changed",
                    'message': f"The ownership of '{self.handover_name}' has been successfully transferred to {self.owner.name}.",
                    'type': 'notification',
                }
            }

    # Action to make unit ready and transition it to Home Orientation
    def action_submit(self):
        for record in self:
            spa_document = record.document_id.filtered(
                lambda d: d.handover_document_id.name == "SPA" and (d.file or d.image))
            if not spa_document:
                raise exceptions.ValidationError(
                    _("You cannot submit without a SPA document containing a file or an image."))

            record.unit_ready = True
            record.orientation_letter_sent = True
            record.state = 'home_orientation'

            # Assign the record to a CRM user
            crm_user = self.env['res.users'].search(
                [('groups_id', 'in', self.env.ref('real_estate_handover.group_crm_user').id)])
            if crm_user:
                # Find the user with the least assigned handover records
                user_handover_counts = {
                    user: self.env['handover.process'].search_count([('owner', '=', user.id)])
                    for user in crm_user
                }
                new_owner = min(user_handover_counts, key=user_handover_counts.get)
                record.owner = new_owner

                # Send Email for Invitation Home Orientation
            template = self.env.ref('real_estate_handover.email_template_home_invitation_orientation',
                                    raise_if_not_found=False)
            if template:
                template.sudo().send_mail(record.id, force_send=True)
            else:
                raise exceptions.UserError(_("Email template not found. Please check if it exists."))
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Unit is Ready successfully!',
                    'type': 'rainbow_man'
                }
            }

    # Send BCC Announcement email using predefined template and mark it as sent
    def action_send_bcc(self):
        for record in self:
            template = self.env.ref('real_estate_handover.email_template_bcc_announcement')
            if template:
                template.send_mail(record.id, force_send=True)
            record.write({'bcc_announcement_sent': True})
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'BCC Announcement sent successfully!',
                    'type': 'rainbow_man'
                }
            }

    # Mark the handover process as completed by updating the state
    def completed_kho_process(self):
        for record in self:
            record.write({'state': 'handover_completed'})
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Handover Completed successfully!',
                    'type': 'rainbow_man'
                }
            }
