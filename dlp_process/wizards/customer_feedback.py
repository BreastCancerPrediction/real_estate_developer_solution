from odoo import models, fields

class CustomerFeedback(models.TransientModel):
    _name = 'customer.feedback'
    _description = 'Customer Feedback'

    rating = fields.Selection([('1', '😠 Very Bad'),('2', '😞 Bad'),('3', '😐 Okay'),('4', '🙂 Good'),
        ('5', '😍Very Good'),], string="Customer Satisfaction Rating",required=True)
    feedback = fields.Text(string="Customer Feedback",required=True)
    signature = fields.Binary(string="Signature",required=True)
    appointment_type_id = fields.Many2one('appointment.type', string="Appointment")

    def action_save(self):
        self.ensure_one()
        appointment_type = self.appointment_type_id
        if appointment_type:
            appointment_type.rating = self.rating
            appointment_type.feedback = self.feedback
            appointment_type.signature = self.signature
            appointment_type.state = 'completed'
            return {'type': 'ir.actions.act_window_close'}