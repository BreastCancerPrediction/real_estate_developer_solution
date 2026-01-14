# -- encoding: utf-8 --
##############################################################################
#
#    Cloud Science Labs (https://www.cloudsciencelabs.com/)
#
##############################################################################
from odoo import models, fields, api, _
import io
import base64
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image
from odoo.exceptions import UserError


class AppointmentAction(models.TransientModel):
    _name = 'buttons.action'
    _description = 'Buttons Action'


    appointment_type_id = fields.Many2one('appointment.type', string="Appointment")
    def action_open_after_rectification(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'After Rectification',
            'res_model': 'after.rectification',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_appointment_type_id': self.appointment_type_id.id,
            },
        }

    def action_open_check_in(self):
        """
        This method opens the wizard and passes the current record's ID
        as the default appointment type ID.
        """
        self.ensure_one()
        wizard_action = {
            'type': 'ir.actions.act_window',
            'name': 'Check IN',
            'res_model': 'customer.availability',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_appointment_type_id': self.appointment_type_id.id,
            },
        }
        return wizard_action

    def action_open_under_scope(self):
        """
        This method opens the wizard and passes the current record's ID
        as the default appointment type ID.
        """
        self.ensure_one()
        wizard_action = {
            'type': 'ir.actions.act_window',
            'name': 'Under Scope',
            'res_model': 'under.scope',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_appointment_type_id': self.appointment_type_id.id,
            },
        }
        return wizard_action

    def action_open_schedule_appointment(self):
        """
        This method opens the wizard and passes the current record's ID
        as the default appointment type ID.
        """
        self.ensure_one()
        wizard_action = {
            'type': 'ir.actions.act_window',
            'name': 'Schedule Appointment',
            'res_model': 'schedule.appointment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_appointment_type_id': self.appointment_type_id.id,
            },
        }
        return wizard_action

    def action_generate_service_document(self):
        self.ensure_one()
        appointment = self.appointment_type_id

        if not appointment.customer.email:
            raise UserError(_("Customer does not have an email address."))

        # Generate PDF report
        report_obj = self.env.ref('dlp_process.action_service_appointment_report')
        pdf_content, content_type = self.env['ir.actions.report']._render_qweb_pdf(report_obj.id, [appointment.id])

        # Create attachment
        filename = f"Service_Appointment_{appointment.sequence_number or appointment.id}.pdf"
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': 'appointment.type',
            'res_id': appointment.id,
            'mimetype': 'application/pdf',
        })

        # Get the email template
        email_template = self.env.ref('dlp_process.email_template_service_appointment')
        if not email_template:
            raise UserError(_("Email template not found!"))

        # Attach PDF to email template and send
        email_values = {
            'attachment_ids': [attachment.id],
        }
        email_template.send_mail(appointment.id, force_send=True, email_values=email_values)

        return {
            'type': 'ir.actions.act_window_close',
        }


    def action_open_customer_feedback(self):
        self.ensure_one()
        wizard_action = {
            'type': 'ir.actions.act_window',
            'name': 'Customer Feedback',
            'res_model': 'customer.feedback',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_appointment_type_id': self.appointment_type_id.id,

            },
        }
        return wizard_action
