from odoo import models, api


class Lead2Opportunity(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        # Set default Sales Team: Property Consultant
        team = self.env['crm.team'].search([('name', '=', 'Property Consultant')], limit=1)
        if team:
            res['team_id'] = team.id

        # Get next user from Property Consultant group
        user = self._get_next_user_from_group()
        if user:
            res['user_id'] = user.id

        return res

    def _get_next_user_from_group(self):
        group = self.env.ref('real_estate_management.group_property_consultant', raise_if_not_found=False)
        if not group:
            return False

        users = self.env['res.users'].search([
            ('groups_id', 'in', group.id),
            ('active', '=', True)
        ])
        if not users:
            return False

        # Round-robin assignment using ir.config_parameter
        param = self.sudo().env['ir.config_parameter']
        last_index = int(param.get_param('property_consultant.last_index', default='-1'))
        next_index = (last_index + 1) % len(users)
        param.set_param('property_consultant.last_index', str(next_index))
        return users[next_index]
