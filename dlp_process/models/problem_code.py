from odoo import fields, api, models



class ProblemCode(models.Model):
    _name = 'problem.code'
    _description = 'Problem Code'

    name = fields.Char(string="Problem Code")
    ticket_id = fields.Many2one('helpdesk.ticket', string="Ticket")
    category = fields.Many2one('category.info', string="Category")
    tag_id = fields.Many2one('helpdesk.tag', related='ticket_id.tag_id', string="Sub-Category", store=True, readonly=False)
    incident_location = fields.Selection(related='ticket_id.incident_location', string="Incident Location", store=True, readonly=False)

    # _sql_constraints = [
    #     ('unique_problem_code', 'unique(name)', 'Problem Code must be unique.')
    # ]