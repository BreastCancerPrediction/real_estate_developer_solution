# -- encoding: utf-8 --
##############################################################################
#
#    Cloud Science Labs (https://www.cloudsciencelabs.com/)
#
##############################################################################
from odoo import models, fields, api, _


class AfterRectification(models.TransientModel):
    _name = 'after.rectification'
    _description = 'After Rectification'

    upload_image = fields.Binary(string="Upload Image",required=True)
    appointment_type_id = fields.Many2one('appointment.type', string="Appointment")


    def action_save_image(self):
        self.ensure_one()
        appointment_type = self.appointment_type_id
        if self.upload_image and appointment_type:
            appointment_type.rectification_image = self.upload_image

