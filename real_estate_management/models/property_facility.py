# -- encoding: utf-8 --
##############################################################################
#
#    Cloud Science Labs
#    Copyright (C) 2024 (https://www.cloudsciencelabs.com/)
#
##############################################################################
from odoo import fields, models


class PropertyFacility(models.Model):
    """A class for the model property facilities to represent
    the related facilities for a property"""
    _name = 'property.facility'
    _description = 'Property Amenities'
    _rec_name = 'facility'

    facility = fields.Text(string='Amenities', required=True,
                           help='Amenities of the property')
