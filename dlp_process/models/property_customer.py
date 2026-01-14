from odoo import fields, api, models


class PropertyCustomer(models.Model):
    _inherit = 'res.partner'

    account_record_type = fields.Char(string="Account Record Type")
    account_type = fields.Char(string="Account Type")
    account_owner = fields.Char(string="Account Owner")
    account_number = fields.Integer(string="Account Number")
    current_home_status = fields.Char(string="Current Home Status")

    # person Information
    country_id = fields.Many2one('res.country', string="Mobile Country")
    mobile_country_code = fields.Char(string="Country Code", compute="_compute_mobile_country_code", store=True)
    alternate_email = fields.Char(string="Alternate Email")
    birth_date = fields.Date(string="Birth Date")
    marital_status = fields.Selection([('single', 'Single'),('married', 'Married'),
    ('divorced', 'Divorced'),('widowed', 'Widowed'),('separated', 'Separated')], string="Marital Status")
    language_preference = fields.Selection([('english', 'English'),('hindi', 'Hindi'),
    ('french', 'French'),('german', 'German'),('spanish', 'Spanish')], string="Language Preference")
    gender = fields.Selection([('male', 'Male'),('female', 'Female'),('other', 'Other')], string="Gender")
    tenant_type = fields.Selection([('individual', 'Individual'),('company', 'Company'),
        ('organization', 'Organization'),('other', 'Other')], string="Tenant Type")
    unit_ids = fields.One2many('product.template', compute='compute_sold_units',string='Sold Units')

    def compute_sold_units(self):
        for partner in self:
            leads = self.env['crm.lead'].search([
                ('partner_id', '=', partner.id),
                ('stage_id.name', '=', 'Sold'),
                ('unit_id', '!=', False)
            ])
            partner.unit_ids = leads.mapped('unit_id')

    def action_view_sold_units(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sold Units',
            'res_model': 'product.template',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.unit_ids.ids)],
        }

    @api.depends('country_id')
    def _compute_mobile_country_code(self):
        for rec in self:
            rec.mobile_country_code = rec.country_id.phone_code if rec.country_id else ''


