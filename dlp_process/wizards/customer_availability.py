from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class CustomerAvailability(models.TransientModel):
    _name = 'customer.availability'
    _description = 'Customer Availability'

    customer_availability = fields.Selection(
        [('available', 'Available'), ('not_available', 'Not Available')],
        string="Customer Availability",
        required=True
    )
    customer_not_availability_image = fields.Binary(string="Customer Not Available Image")
    appointment_type_id = fields.Many2one('appointment.type', string="Appointment")
    checkin_time = fields.Datetime(string="Checkin Time", required=True)


    @api.constrains('customer_availability', 'customer_not_availability_image')
    def _check_image_required_if_not_available(self):
        for record in self:
            if record.customer_availability == 'not_available' and not record.customer_not_availability_image:
                raise ValidationError("Please upload an image if the customer is not available.")


    def action_apply_availability(self):
        self.ensure_one()
        appointment_type = self.appointment_type_id
        if appointment_type:
            appointment_type.customer_availability = self.customer_availability
            appointment_type.customer_not_availability_image = self.customer_not_availability_image
            appointment_type.checkin_time = self.checkin_time

            if self.customer_availability == 'not_available':
                appointment_type.state = 'completed'

                template = self.env.ref('dlp_process.email_template_customer_not_available', raise_if_not_found=False)
                if template:
                    template.send_mail(appointment_type.id, force_send=True)

            return {'type': 'ir.actions.act_window_close'}
        else:
            raise UserError(_("No Appointment Type found in context."))
