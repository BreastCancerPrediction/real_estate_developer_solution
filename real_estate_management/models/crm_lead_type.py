# -- encoding: utf-8 --
##############################################################################
#
#    Cloud Science Labs
#    Copyright (C) 2024 (https://www.cloudsciencelabs.com/)
#
##############################################################################
from odoo import models, fields, api, _


class CrmLeadType(models.Model):
    _name = 'crm.lead.type'
    _description = 'Crm Lead Type'

    name = fields.Char(string="Name")