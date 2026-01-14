from odoo import fields, api, models
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class ServiceAppointment(models.Model):
    _inherit = 'appointment.type'

    customer = fields.Many2one('res.partner', "Customer")
    customer_availability = fields.Selection(
        [('available', 'Available'), ('not_available', 'Not Available')],
        string="Customer Availability"
    )
    sequence_number = fields.Char(string='Sequence', readonly=True, copy=False)
    under_scope = fields.Selection(
        [('under_dlp_scope', 'Under DLP Scope'), ('not_under_dlp_scope', 'Not Under DLP Scope')],
        string="Under Scope"
    )
    upload_image = fields.Binary(string="Under Scope Image")
    rectification_image = fields.Binary(string="Rectification Image")
    under_scope_image = fields.Binary(string="Under Scope Image")
    filename = fields.Char(string="Filename")
    appointment_start_date = fields.Datetime(string="Appointment Start Date")
    appointment_end_date = fields.Datetime(string="Appointment End Date")
    duration = fields.Float(string="Duration (Hours)", compute='_compute_duration', store=True)
    resource = fields.Selection([('self', 'Self'), ('contractor', 'Contractor'), ('both', 'Both')], string="Resource")
    state = fields.Selection([('dispatch', 'Dispatched'), ('not_responding', 'Not Responding'), ('not_checked_in', 'Not Checked In'),('completed', 'Completed'), ], string="Status", default='dispatch', required=True)
    rating = fields.Selection([('1', 'Very Bad'), ('2', 'Bad'), ('3', 'Okay'), ('4', 'Good'), ('5', 'Very Good'), ],string="Customer Satisfaction Rating")
    feedback = fields.Text(string="Customer Feedback")
    signature = fields.Binary(string="Signature")
    workorder_id = fields.Many2one('helpdesk.ticket', string="Work Order")
    checkin_time = fields.Datetime(string="Agent Checkin Time")
    customer_not_availability_image = fields.Binary(string="Customer Not Available Image")

    @api.depends('appointment_start_date', 'appointment_end_date')
    def _compute_duration(self):
        for rec in self:
            if rec.appointment_start_date and rec.appointment_end_date:
                time = rec.appointment_end_date - rec.appointment_start_date
                rec.duration = time.total_seconds() / 3600
            else:
                rec.duration = 0.0

    def action_open_wizard(self):
            """
            This method opens the wizard and passes the current record's ID
            as the default appointment type ID.
            """
            self.ensure_one()
            wizard_action = {
                'type': 'ir.actions.act_window',
                'name': 'Actions',
                'res_model': 'buttons.action',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_appointment_type_id': self.id,
                },
            }
            return wizard_action


    @api.model
    def create(self, vals):
        if not vals.get('sequence_number'):
            vals['sequence_number'] = self.env['ir.sequence'].next_by_code('service.appointment') or 'New'
        appointment = super(ServiceAppointment, self).create(vals)
        return appointment

    def write(self, vals):
        staff_updated = 'staff_user_ids' in vals
        result = super(ServiceAppointment, self).write(vals)
        if staff_updated:
            for rec in self:
                rec._send_email_notification() 
        return result

    @api.model
    def _send_email_notification(self):
        subject = f"New Service Appointment Assigned: {self.name}"
        for user in self.staff_user_ids:
            body_html = f"""
            <p>Hello {user.name},</p>
            <p>You have been assigned to a new Service Appointment: 
                <strong>{self.name}</strong>.
            </p>
            <p>Best Regards,</p>
            <p>Your Company</p>
            <p>{self.env.user.company_id.name}</p>
            """
            email_values = {
                'subject': subject,
                'body_html': body_html,
                'email_from': self.env.user.email or 'info@example.com',
                'email_to': user.email,
            }
            mail = self.env['mail.mail'].create(email_values)
            mail.send()

    @api.model
    def _auto_mark_not_checked_in(self):
        now = fields.Datetime.now()
        grace_period = timedelta(minutes=2)
        appointments = self.search([
            ('state', '=', 'dispatch'),
            ('checkin_time', '=', False),
            ('appointment_start_date', '!=', False),
            ('appointment_start_date', '<=', now - grace_period),
        ])
        for appointment in appointments:
            appointment.state = 'not_checked_in'

