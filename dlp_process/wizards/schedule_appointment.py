# -- encoding: utf-8 --
##############################################################################
#
#    Cloud Science Labs (https://www.cloudsciencelabs.com/)
#
##############################################################################
from odoo import models, fields, api, _


class ScheduleAppointment(models.TransientModel):
    _name = 'schedule.appointment'
    _description = 'Schedule Appointment'

    appointment_start_date = fields.Date(string="Appointment Start Date",required=True)
    appointment_end_date = fields.Date(string="Appointment End Date",required=True)
    resource = fields.Selection( [('self', 'Self'), ('contractor', 'Contractor'),('both','Both')],
                                 string="Resource",required=True)

    appointment_type_id = fields.Many2one('appointment.type', string="Appointment")

    def action_update_appointment(self):
        self.ensure_one()

        # Update the existing appointment record
        if self.appointment_type_id:
            self.appointment_type_id.write({
                'appointment_start_date': self.appointment_start_date,
                'appointment_end_date': self.appointment_end_date,
                'resource': self.resource,
            })

            # Create a new appointment record
            new_appointment = self.env['appointment.type'].create({
                'name': self.appointment_type_id.name,
                'appointment_start_date': self.appointment_start_date,
                'appointment_end_date': self.appointment_end_date,
                'resource': self.resource,
                'customer': self.appointment_type_id.customer.id,
                'customer_availability': self.appointment_type_id.customer_availability,
                'under_scope': self.appointment_type_id.under_scope,
                'under_scope_image': self.appointment_type_id.under_scope_image,
                'customer_not_availability_image': self.appointment_type_id.customer_not_availability_image,
                'state': 'dispatch',
            })

            return {
                'type': 'ir.actions.act_window',
                'name': _('Created Appointment'),
                'res_model': 'appointment.type',
                'view_mode': 'form',
                'res_id': new_appointment.id,
                'target': 'current',
            }

