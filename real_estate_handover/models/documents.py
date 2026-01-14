# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class Documents(models.Model):
    _name = 'documents.attachment'
    _description = 'Handover Attachment'

    # Documents Fields inside Handover
    handover_id = fields.Many2one('handover.process',string="Name")
    handover_document_id = fields.Many2one('handover.documents',string="Document Name")
    file = fields.Binary(string='File',attachment=True)
    filename = fields.Char(string="Filename")
    image = fields.Binary(string='Image',attachment=True)
    image_name = fields.Char(string="Image Name")