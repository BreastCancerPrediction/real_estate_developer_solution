from odoo import fields, api, models



class IncidentDescription(models.Model):
    _name = 'incident.description'
    _description = 'Incident Description'

    name = fields.Char(string="Incident Description")
    helpdesk_tag_id = fields.Many2one('helpdesk.tag', string="Helpdesk Tag")