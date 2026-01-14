# -- encoding: utf-8 --
##############################################################################
#
#    Cloud Science Labs
#    Copyright (C) 2024 (https://www.cloudsciencelabs.com/)
#
##############################################################################
from odoo import fields, models


class PropertyDashboard(models.Model):
    _name = 'property.dashboard'
    _description = 'Property Dashboard'
    
    def get_details(self):
        total_property = self.env['property.property'].search_count([])
        sold_property = self.env['property.property'].search_count([('status', '=', 'sold')])
        return {
            'total_property': total_property,
            'sold_property': sold_property,
        }