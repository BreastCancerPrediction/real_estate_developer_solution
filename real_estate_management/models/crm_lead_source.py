# -- encoding: utf-8 --
##############################################################################
#
#    Cloud Science Labs
#    Copyright (C) 2024 (https://www.cloudsciencelabs.com/)
#
##############################################################################
from odoo import models, fields, api, _


class CrmLeadSource(models.Model):
    _name = 'crm.lead.source'
    _description = 'Crm Lead Source'

    name = fields.Char(string="Name")