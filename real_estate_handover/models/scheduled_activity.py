# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ScheduledActivity(models.TransientModel):
    _inherit = 'mail.activity.schedule'

    type = fields.Selection(
        [("none", "None"), ("email", "Email"), ("meeting", "Meeting"), ("other", "Other"), ("call", "Call"),
         ("home_orientation_appointment", "Home Orientation Appointment"), ("kho_appointment", "KHO Appointment")],
        default="none", string="Type")


    def create(self, vals):
        res = super(ScheduledActivity, self).create(vals)

        if vals.get('type') == 'home_orientation_appointment':
            handover_record = self.env['handover.process'].browse(self.env.context.get('active_id'))
            if handover_record and handover_record.customer_availability_for_cho != 'customer_available':
                raise ValidationError(
                    "You cannot schedule a meeting unless Customer Availability For CHO is set to 'Customer Available'."
                )
            handover_record.is_appointment_booked = True
            handover_record.write({'state': 'appointment'})

            # assignment for HO Agent users
            ho_agents = self.env['res.users'].search([
                ('groups_id', 'in', self.env.ref('real_estate_handover.group_ho_agent').id)
            ])
            if ho_agents:
                # Get the user with the least assigned handover records
                user_handover_counts = {
                    user: self.env['handover.process'].search_count([('owner', '=', user.id)])
                    for user in ho_agents
                }
                new_owner = min(user_handover_counts, key=user_handover_counts.get)
                handover_record.owner = new_owner


        if vals.get('type') == 'meeting':
            handover_record = self.env['handover.process'].browse(self.env.context.get('active_id'))
            if handover_record:
                # Fetch users in treasure team group
                treasure_team_users = self.env['res.users'].search([
                    ('groups_id', 'in', self.env.ref('real_estate_handover.group_treasure_team').id)
                ])

                if treasure_team_users:
                    new_owner = min(treasure_team_users, key=lambda user: self.env['handover.process'].search_count(
                        [('owner', '=', user.id)]
                    ))
                    handover_record.owner = new_owner

                    template = self.env.ref('real_estate_handover.email_template_home_invitation_orientation')
                    if template:
                        template.send_mail(handover_record.id, force_send=True)


        if vals.get('type') == 'kho_appointment':
            handover_record = self.env['handover.process'].browse(self.env.context.get('active_id'))
            if handover_record:
                handover_record.sudo().write({'state': 'kho_appointment'})

                template = self.env.ref('real_estate_handover.email_template_for_confirmation_of_home_orientation')
                if template:
                    # Find ADDC document
                    addc_docs = handover_record.document_id.filtered(
                        lambda d: d.handover_document_id.name == 'ADDC'
                    )
                    attachment_ids = []
                    for doc in addc_docs:
                        binary_data = doc.file or doc.image
                        filename = doc.filename or doc.image_name or 'attachment.dat'
                        if binary_data:
                            ir_attachment = self.env['ir.attachment'].create({
                                'name': filename,
                                'type': 'binary',
                                'datas': binary_data,
                                'res_model': 'handover.process',
                                'res_id': handover_record.id,
                            })
                            attachment_ids.append(ir_attachment.id)

                    # Send email with attachments
                    template.send_mail(
                        handover_record.id,
                        force_send=True,
                        email_values={'attachment_ids': [(6, 0, attachment_ids)]}
                    )

        return res

    def write(self, vals):
        res = super(ScheduledActivity, self).write(vals)

        if vals.get('type') == 'home_orientation_appointment':
            handover_record = self.env['handover.process'].browse(self.env.context.get('active_id'))
            if handover_record and handover_record.customer_availability_for_cho != 'customer_available':
                raise ValidationError(
                    "You cannot schedule a meeting unless Customer Availability For CHO is set to 'Customer Available'."
                )
            handover_record.is_appointment_booked = True
            handover_record.write({'state': 'appointment'})

            #assignment for group_ho_agent users
            ho_agents = self.env['res.users'].search([
                ('groups_id', 'in', self.env.ref('real_estate_handover.group_ho_agent').id)
            ])
            if ho_agents:
                # Get the user with the least assigned handover records
                user_handover_counts = {
                    user: self.env['handover.process'].search_count([('owner', '=', user.id)])
                    for user in ho_agents
                }
                new_owner = min(user_handover_counts, key=user_handover_counts.get)
                handover_record.owner = new_owner

        if vals.get('type') == 'meeting':
            handover_record = self.env['handover.process'].browse(self.env.context.get('active_id'))
            if handover_record:
                # Fetch users in government team group
                treasure_team_users = self.env['res.users'].search([
                    ('groups_id', 'in', self.env.ref('real_estate_handover.group_treasure_team').id)
                ])

                if treasure_team_users:
                    new_owner = min(treasure_team_users, key=lambda user: self.env['handover.process'].search_count(
                        [('owner', '=', user.id)]
                    ))
                    handover_record.owner = new_owner

        if vals.get('type') == 'kho_appointment':
            handover_record = self.env['handover.process'].browse(self.env.context.get('active_id'))
            if handover_record:
                handover_record.sudo().write({'state': 'kho_appointment'})

                template = self.env.ref('real_estate_handover.email_template_for_confirmation_of_home_orientation')
                if template:
                    # Find ADDC document
                    addc_docs = handover_record.document_id.filtered(
                        lambda d: d.handover_document_id.name == 'ADDC'
                    )
                    attachment_ids = []
                    for doc in addc_docs:
                        binary_data = doc.file or doc.image
                        filename = doc.filename or doc.image_name or 'attachment.dat'
                        if binary_data:
                            ir_attachment = self.env['ir.attachment'].create({
                                'name': filename,
                                'type': 'binary',
                                'datas': binary_data,
                                'res_model': 'handover.process',
                                'res_id': handover_record.id,
                            })
                            attachment_ids.append(ir_attachment.id)

                    # Send email with attachments
                    template.send_mail(
                        handover_record.id,
                        force_send=True,
                        email_values={'attachment_ids': [(6, 0, attachment_ids)]}
                    )

        return res