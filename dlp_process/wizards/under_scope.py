# -- encoding: utf-8 --
##############################################################################
#
#    Cloud Science Labs (https://www.cloudsciencelabs.com/)
#
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class UnderScope(models.TransientModel):
    _name = 'under.scope'
    _description = 'Under Scope'

    under_scope = fields.Selection(
        [('under_dlp_scope', 'Under DLP Scope'), ('not_under_dlp_scope', 'Not Under DLP Scope')],
        string="Under Scope"
    )
    upload_image = fields.Binary(string="Upload Image")
    upload_image_not = fields.Binary(string="Upload Image")

    show_upload_image_dlp = fields.Boolean(string="Show Upload Image")
    show_upload_image_not_dlp = fields.Boolean(string="Show Upload Image")
    appointment_type_id = fields.Many2one('appointment.type', string="Appointment")


    @api.onchange('under_scope')
    def _onchange_under_scope(self):
        self.show_upload_image_dlp = self.under_scope == 'under_dlp_scope'
        self.show_upload_image_not_dlp = self.under_scope == 'not_under_dlp_scope'

    @api.constrains('under_scope', 'upload_image', 'upload_image_not')
    def _check_required_images(self):
        for record in self:
            if not record.under_scope:
                raise ValidationError("Please select the Under Scope option.")
            if record.under_scope == 'under_dlp_scope' and not record.upload_image:
                raise ValidationError("Please upload the image for DLP Scope")
            if record.under_scope == 'not_under_dlp_scope' and not record.upload_image_not:
                raise ValidationError("Please upload the image for Not Under DLP Scope.")

    def action_under_scope(self):
        self.ensure_one()
        appointment_type = self.appointment_type_id
        if not appointment_type:
            raise UserError(_("No Appointment Type found."))

        appointment_type.under_scope = self.under_scope

        if self.under_scope == 'under_dlp_scope' and self.upload_image:
            appointment_type.under_scope_image = self.upload_image

        elif self.under_scope == 'not_under_dlp_scope' and self.upload_image_not:
            appointment_type.under_scope_image = self.upload_image_not

            # Send mail using template
            template = self.env.ref('dlp_process.email_template_under_scope')
            if template and appointment_type.customer and appointment_type.customer.email:
                template.send_mail(appointment_type.id, force_send=True)

            appointment_type.state = 'completed'


        return {'type': 'ir.actions.act_window_close'}
