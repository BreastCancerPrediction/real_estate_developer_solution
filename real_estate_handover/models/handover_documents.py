# -- encoding: utf-8 --
##############################################################################
#
#    Cloud Science Labs
#    Copyright (C) 2024 (https://www.cloudsciencelabs.com/)
#
##############################################################################
from odoo import models, fields, api, _


class HandoverDocuments(models.Model):
    _name = 'handover.documents'
    _description = 'HandoverDocuments'

    name = fields.Char(string="Name")
