from odoo import fields, api, models
from datetime import datetime, timedelta


class Dlp_process(models.Model):
    _inherit = 'helpdesk.ticket'

    appointment_count = fields.Integer(string="Appointment Count", compute="compute_appointment_count")
    Work_order_no = fields.Char(string="Work Order Number", copy=False, readonly=True, index=True)
    type_of_incident = fields.Selection([('new', 'New'),('follow_up', 'Follow Up'),
        ('emergency', 'Emergency'),('scheduled', 'Scheduled'),('recurring', 'Recurring') ], string="Type of Incident")
    category = fields.Many2one('category.info', string="Category")
    incident_description_id = fields.Many2one('incident.description', string="Incident Description", readonly=True)
    tag_id = fields.Many2one('helpdesk.tag', string="Sub-Category")
    resolution_typology = fields.Selection([('repair', 'Repair'),('replacement', 'Replacement'),
        ('refund', 'Refund'),('maintenance', 'Maintenance'),('other', 'Other')], string="Resolution Typology")
    is_emergency = fields.Boolean(string="Is Emergency")
    due_date = fields.Char(string="Due Date")
    incident_location = fields.Selection([('master_bedroom', 'Master Bedroom'),
        ('maids_bedroom', 'Maids Bedroom'),('kitchen', 'Kitchen'),
        ('living_room', 'Living Room'),('bathroom', 'Bathroom'),
        ('balcony', 'Balcony')], string="Incident Location")
    problem_code = fields.Char(string="Problem Code")
    resolution_description = fields.Text(string="Resolution Description")
    requester = fields.Selection([('owner', 'Owner'),
        ('tenant', 'Tenant'),('representative', 'Representative')], string="Requester")
    requester_email = fields.Char(string="Requester Email")
    requester_comment = fields.Text(string="Requester Comment")
    requester_name = fields.Many2one('res.partner', string="Requester Name")
    requester_phone = fields.Char(string="Requester Phone")
    unit_id = fields.Many2one('product.template', string="Unit")
    contractor = fields.Char(string="Contractor")
    account = fields.Many2one('res.partner', string="Account")
    case = fields.Char(string="Case")
    customer_comment = fields.Text(string="Customer Comment")
    rating = fields.Selection([('0', 'Low'),('1', 'Very Low'),('2', 'Medium'),('3', 'High')], string="Rating")
    appointment_ids = fields.One2many('appointment.type', 'workorder_id', string="Appointments")
    user_id = fields.Many2one('res.users', string="Assign To")
    is_my_request = fields.Boolean(
        string="Is My Request",
        compute="_compute_is_my_request",
        store=True,  # Make it stored
        index=True  # Optional: improves performance
    )
    @api.model
    def get_tiles_data(self, filter_by=None):
        today = fields.Date.context_today(self)
        ticket_domain = []


        if filter_by == 'this_week':
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
            ticket_domain = [('create_date', '>=', start), ('create_date', '<=', end)]

        elif filter_by == 'last_week':
            end = today - timedelta(days=today.weekday() + 1)
            start = end - timedelta(days=6)
            ticket_domain = [('create_date', '>=', start), ('create_date', '<=', end)]

        elif filter_by == 'this_month':
            start = today.replace(day=1)
            next_month = (start + timedelta(days=31)).replace(day=1)
            end = next_month - timedelta(days=1)
            ticket_domain = [('create_date', '>=', start), ('create_date', '<=', end)]



        service_domain = []
        dlp_domain = []

        if filter_by:
            service_domain = [('create_date', '>=', start), ('create_date', '<=', end)]
            dlp_domain = [('create_date', '>=', start), ('create_date', '<=', end)]
        all_workorders = self.env['helpdesk.ticket'].search(ticket_domain)
        service_appointments = self.env['appointment.type'].search(service_domain)
        dlp_cases = self.env['dlp.case'].search(dlp_domain)


        stage_data = self.get_workorder_stage_counts(ticket_domain)
        resolution_data = self.get_resolution_typology_data(ticket_domain)
        # Get priority distribution using the filtered domain
        priority_data = self.env['helpdesk.ticket'].read_group(
            domain=ticket_domain,
            fields=['priority'],
            groupby=['priority']
        )

        priority_map = {
            '0': 'Low',
            '1': 'Medium',
            '2': 'High',
            '3': 'Very High',
        }

        priority_labels = []
        priority_counts = []

        for rec in priority_data:
            key = rec['priority']
            label = priority_map.get(key, 'Unknown')
            priority_labels.append(label)
            priority_counts.append(rec['priority_count'])


        return {
            'all_workorder_count': len(all_workorders),
            'service_appointment_count': len(service_appointments),
            'dlp_case_count': len(dlp_cases),
            'stage_labels': stage_data['labels'],
            'stage_counts': stage_data['counts'],
            'typology_labels': resolution_data['labels'],
            'typology_counts': resolution_data['counts'],
            'priority_labels': priority_labels,
            'priority_counts': priority_counts,
        }

    def get_workorder_stage_counts(self, domain=None):
        domain = domain or []

        grouped_data = self.env['helpdesk.ticket'].read_group(
            domain=domain,
            fields=['stage_id'],
            groupby=['stage_id']
        )

        stage_mapping = {
            'New': 0,
            'In Progress': 0,
            'Solved': 0,
            'Cancelled': 0,
        }

        for group in grouped_data:
            stage_id = group.get('stage_id')
            count = group.get('stage_id_count', 0)
            if stage_id:
                stage_name = stage_id[1]
                if stage_name in stage_mapping:
                    stage_mapping[stage_name] = count

        return {
            'labels': list(stage_mapping.keys()),
            'counts': list(stage_mapping.values())
        }
    def get_resolution_typology_data(self, domain=None):
        domain = domain or []

        typology_data = self.env['helpdesk.ticket'].read_group(
            domain=domain,
            fields=['resolution_typology'],
            groupby=['resolution_typology']
        )

        typology_label_map = {
            'repair': 'Repair',
            'replacement': 'Replacement',
            'refund': 'Refund',
            'maintenance': 'Maintenance',
            'other': 'Other'
        }

        labels = []
        counts = []

        for record in typology_data:
            key = record['resolution_typology']
            label = typology_label_map.get(key, 'Unknown')
            labels.append(label)
            counts.append(record['resolution_typology_count'])

        return {
            'labels': labels,
            'counts': counts,
        }


    @api.depends('requester_name')
    def _compute_is_my_request(self):
        current_partner = self.env.user.partner_id
        for rec in self:
            rec.is_my_request = rec.requester_name == current_partner

    @api.onchange('requester', 'account')
    def _onchange_requester(self):
        if self.requester == 'owner' and self.account:
            self.requester_name = self.account.id
            self.requester_phone = self.account.phone
            self.requester_email = self.account.email
        else:
            self.requester_name = ''
            self.requester_phone = ''
            self.requester_email = ''

    def write(self, vals):
        if 'priority' in vals:
            vals = self._compute_due_date(vals)
        res = super(Dlp_process, self).write(vals)

        # Check if stage_id changed to Solved or Cancelled
        if 'stage_id' in vals:
            solved_stage = self.env.ref('helpdesk.stage_solved', raise_if_not_found=False)
            cancelled_stage = self.env.ref('helpdesk.stage_cancelled', raise_if_not_found=False)
            for ticket in self:
                if ticket.stage_id in (solved_stage, cancelled_stage):
                    # Find the related DLP case
                    dlp_case = self.env['dlp.case'].search([('seq_num', '=', ticket.case)], limit=1)
                    if dlp_case:
                        dlp_case.write({'status': 'closed', 'date_time_close': fields.Datetime.now()})
        return res

    def _compute_due_date(self, vals):
        priority = vals.get('priority')
        if priority:
            if priority == '3':  # Urgent
                vals['due_date'] = "Within 2 hours"
            elif priority == '2':  # High
                vals['due_date'] = "Within 1 day"
            elif priority == '1':  # Medium
                vals['due_date'] = "Within 3 days"
            else:  # Low
                vals['due_date'] = "Within 5 days"
        return vals

    @api.model
    def create(self, vals):
        vals = self._compute_due_date(vals)
        if vals.get('Work_order_no', 'New') == 'New':
            vals['Work_order_no'] = self.env['ir.sequence'].sudo().next_by_code('work.order') or 'New'

        ticket = super(Dlp_process, self).create(vals)

        # Create a corresponding appointment type record
        self.env['appointment.type'].sudo().create({
            'name': ticket.name,
            'customer': ticket.account.id if ticket.account else False,
            'workorder_id': ticket.id
        })

        # Map ticket priority to DLP case priority
        PRIORITY_MAP = {'0': 'low', '1': 'medium', '2': 'high', '3': 'urgent'}

        # Create a corresponding DLP case record
        dlp_case = self.env['dlp.case'].sudo().create({
            'case_record_type': 'defect_liability_complaint',
            'case_origin': 'Work Order',
            'work_order_status': ticket.stage_id.name,
            'work_order_incident_description': ticket.incident_description_id.name,
            'work_order_account': ticket.account.id if ticket.account else None,
            'work_order_subject': ticket.name,
            'wo_type_of_incident': ticket.type_of_incident,
            'wo_resolution_priority': PRIORITY_MAP.get(ticket.priority, False),
            'wo_resolution_typology': ticket.resolution_typology or '',
            'wo_category': ticket.category.name if ticket.category else '',
            'wo_sub_category': ticket.tag_id.name if ticket.tag_id else '',
            'wo_location': ticket.incident_location or '',
            'wo_currency_code': self.env.company.currency_id.name if self.env.company.currency_id else '',
            'date_time_open': fields.Datetime.now(),
            'requestor_name': ticket.account.id if ticket.account else None,
            'requestor_email': ticket.account.email if ticket.account else '',
            'requestor_phone': ticket.account.phone if ticket.account else '',
            'requestor_unit': ticket.unit_id.id if ticket.unit_id else None,
        })

        # Set the DLP case number in helpdesk ticket
        ticket.case = dlp_case.seq_num

        # Post a message in the Chatter
        ticket.message_post(
            body="Service Appointment created for %s" % (ticket.Work_order_no),
            message_type="notification",
        )

        return ticket

    @api.depends('name')
    def compute_appointment_count(self):
        for ticket in self:
            ticket.appointment_count = self.env['appointment.type'].search_count([('name', '=', ticket.name)])

    def action_view_appointments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Appointment Type',
            'res_model': 'appointment.type',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': [('name', '=', self.name)],
        }

    @api.onchange('category', 'tag_id', 'incident_location')
    def _onchange_fill_problem_code(self):
        if self.category and self.tag_id and self.incident_location:
            code = self.env['problem.code'].search([
                ('category', '=', self.category.id),
                ('tag_id', '=', self.tag_id.id),
                ('incident_location', '=', self.incident_location)
            ], limit=1)
            self.problem_code = code.name if code else False

    @api.onchange('tag_id')
    def _onchange_helpdesk_tag(self):
        if self.tag_id:
            tag_id = self.tag_id.ids
            descriptions = self.env['incident.description'].search([('helpdesk_tag_id', 'in', tag_id)])
            return {
                'domain': {'incident_description_id': [('helpdesk_tag_id', 'in', tag_id)]},
                'value': {
                    'incident_description_id': descriptions[0].id if descriptions else False
                }
            }
        else:
            return {
                'domain': {'incident_description_id': []},
                'value': {'incident_description_id': False}
            }

    @api.onchange('category')
    def _onchange_category(self):
        if self.category:
            return {
                'domain': {
                    'tag_id': [('category_id', '=', self.category.id)]
                }
            }
        else:
            return {
                'domain': {
                    'tag_id': []
                }
            }

    @api.model
    def _auto_close_work_orders(self):
        two_days_ago = fields.Datetime.now() - timedelta(days=2)
        close_stage = self.env['work.order.stage'].search([('name', '=', 'close')], limit=1)
        if not close_stage:
            return 
        work_orders = self.search([
            ('stage_id', '!=', close_stage.id),
            ('appointment_ids', '!=', False),
        ])
        for wo in work_orders:
            stale_appointments = wo.appointment_ids.filtered(
                lambda a: a.state == 'customer_not_responding' and a.write_date <= two_days_ago
            )
            if stale_appointments:
                wo.stage_id = close_stage.id




class HelpdeskTag(models.Model):
    _inherit = 'helpdesk.tag'

    category_id = fields.Many2one('category.info', string="Category")

