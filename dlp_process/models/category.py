from odoo import fields, api, models



class Category(models.Model):
    _name = 'category.info'
    _description = 'Category Information'

    name = fields.Char(string="Category")
