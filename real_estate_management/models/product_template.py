# -- encoding: utf-8 --
##############################################################################
#
#    Cloud Science Labs
#    Copyright (C) 2024 (https://www.cloudsciencelabs.com/)
#
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'


    is_product = fields.Boolean(string="Is Product")
    is_unit = fields.Boolean(default=True)
    sap_unit_number = fields.Char(string='SAP Unit Number', readonly=False, copy=False)
    property_name = fields.Many2one('property.property', string="Property")
    floor_id = fields.Many2one('product.floor',string='Floor')
    property_type = fields.Selection(
        [("residential", "Residential"),("commercial", "Commercial"),],
        string="Type",help="The type of the property")
    unit_type_id = fields.Many2one('unit.type', string="Unit Type", help="Type of unit")
    lease_unit_type = fields.Selection([('management', 'Management'),('rental', 'Rental')],
        string="Lease Unit Type")
    square_feet = fields.Integer(string="Square Feet")
    rent_group = fields.Char(string="Rent Group")
    active_status = fields.Boolean(string="Active Status")
    late_fee = fields.Float(string="Late Fee")
    current_vacancy = fields.Boolean(string="Current Vacancy")
    management_vacanct_unit = fields.Char(string="Management Vacanct Unit")
    use_unit_utilities = fields.Boolean(string="Use Unit Utilities")
    parkings = fields.Boolean(string="Parkings")
    street = fields.Char(string="Street", help="The street name")
    street2 = fields.Char(string="Street2", help="The street2 name")
    zip = fields.Char(string="Zip", change_default=True, help="Zip code for the place")
    city = fields.Char(string="City", help="The name of the city")
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        ondelete="restrict",
        help="The name of the country",
    )
    state_id = fields.Many2one(
        "res.country.state",
        string="State",
        ondelete="restrict",
        tracking=True,
        domain="[('country_id', '=?', country_id)]",
        help="The name of the state",
    )
    status = fields.Selection([
        ('vacant', 'Vacant'),
        ('assign', 'Assign'),
        ('booked', 'Booked'),
        ('occupied', 'Occupied')],
        default="vacant",
        string="Status",
        copy=False)
    property_status = fields.Selection([
        ('available', 'Available'),
        ('pre_booked', 'Pre-Booked'),
        ('unassigned', 'Unassigned'),
        ('ready_to_release', 'Ready to Release'),
        ('under_construction', 'Under Construction'),
        ('sold', 'Sold'),
        ('under_maintenance', 'Under Maintenance')],
        string="Property Status")

    possession = fields.Selection([
        ('6', 'Six Months'),
        ('12', 'One Year'),
        ('24', 'Two Years'),
    ],string="Possession with in")
    # One2many relation to product.utility
    utility_ids = fields.One2many('product.utility.line', 'utility_id', string="Utilities")
    total_price = fields.Float(string="Total Price of Utilities", compute="_compute_total_price", store=True)
    floor = fields.Many2one('property.floor', string="Floor")
    aminities_count = fields.Integer(compute="action_aminities_count")
    total_unit_price = fields.Float(string = "Unit Price + Utilitie Price + Vat Amount", compute="compute_total_unit_price")
    unit_price = fields.Float(string="Price Per Unit")
    check_readonly = fields.Boolean(default=False)
    completion_date = fields.Date(string="Completion Date")
    unit_category = fields.Selection([
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('studio', 'Studio'),
        ('penthouse', 'Penthouse')
    ], string="Unit Category")
    project_manager = fields.Many2one('res.users', string="Project Manager")
    tax_id = fields.Many2one('account.tax', string="Tax")
    parking_ids = fields.One2many('product.parking', 'parking_id', string="Parkings")
    #property Information
    number_of_bedroom = fields.Integer(string="Number Of Bedroom")
    number_of_study_room = fields.Integer(string="Number Of Study Room")
    number_of_servent_room = fields.Integer(string="Number Of Servent Room")
    number_of_bathroom = fields.Integer(string="Number Of Bathroom")
    number_of_store_room = fields.Integer(string="Number Of Store Room")
    number_of_balcony = fields.Integer(string="Number Of Balcony")
    vat_tax = fields.Float(string="Vat Amount", compute="compute_vat_tax", store=True, help="Tax id(Amount) if Tax id")
    payment_plan = fields.Many2one('product.subscription.period', string="Payment Plan")
    is_storable = fields.Boolean(string='Is Storable', default=True)

    def action_work_order(self):
        self.ensure_one()
        crm_lead = self.env['crm.lead'].search([
            ('unit_id', '=', self.id),
            ('stage_id.name', '=', 'Sold'),
            ('partner_id', '!=', False)
        ], limit=1)

        if not crm_lead:
            raise ValidationError("Cannot create Work Order: the unit must be in 'Sold'.")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Work Order',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_unit_id': self.id,
                'default_account': crm_lead.partner_id.id if crm_lead else False,
            },
        }

    # Compute VAT tax based on unit price and tax percentage
    @api.depends('unit_price', 'tax_id')
    def compute_vat_tax(self):
        for record in self:
            if record.tax_id and record.tax_id.amount_type == 'percent':
                record.vat_tax = (record.unit_price * record.tax_id.amount) / 100
            else:
                record.vat_tax = 0.0

    # Assign SAP Unit Number automatically using sequence during record creation
    @api.model
    def create(self, vals):
        if not vals.get('sap_unit_number'):
            vals['sap_unit_number'] = self.env['ir.sequence'].next_by_code(
                'real_estate_management.sap_unit_number') or '/'

        product = super(ProductTemplate, self).create(vals)
        location = self.env.ref('stock.stock_location_stock')

        if product.type == 'consu':
            for variant in product.product_variant_ids:
                quant = self.env['stock.quant'].create({
                    'product_id': variant.id,
                    'location_id': location.id,
                    'inventory_quantity': 1,
                    'product_uom_id': variant.uom_id.id,
                })
                quant._apply_inventory()

        return product

    @api.depends('utility_ids.price', 'unit_price')
    def compute_total_unit_price(self):
        for record in self:
            record.total_unit_price = record.unit_price + record.total_price + record.vat_tax

    def name_get(self):
        return [(product.id, '%s-%s-%s' % (product.name, product.floor.name, product.property_name.name)) for product in self]

    @api.depends('utility_ids.price')
    def _compute_total_price(self):
        for record in self:
            record.total_price = sum(utility.price for utility in record.utility_ids)

    def action_aminities_count(self):
        self.aminities_count = self.env['property.facility'].search_count([])

    def action_view_aminities(self):
        aminities = self.env['property.facility'].search([])
        action = self.env.ref('real_estate_management.property_facility_action').read()[0]
        lst = []
        for order in aminities:
            lst.append(order.id)
        action['domain'] = [('id', 'in', lst)]
        return action


class ProductUtilityLine(models.Model):
    _name = 'product.utility.line'
    _description = 'Product Utility Line'

    name = fields.Char(string="Utility Name", required=True)
    description = fields.Text(string="Description")
    price = fields.Float(string="Price")
    utility_id = fields.Many2one('product.template', string="Utility")

class UnitType(models.Model):
    _name = 'unit.type'
    _description = 'Unit Type'

    name = fields.Char(string="Unit Type", required=True)

class Parkings(models.Model):
    _name = 'product.parking'
    _description = 'Product Parking'

    name = fields.Char(string="Parking Name")
    parking_number = fields.Char(string="Parking Number")
    type = fields.Selection([("car_parking", "Car Parking"),("bike_parking","Bike Parking")],string="Type")
    Location = fields.Char(string="Location")
    property_name = fields.Many2one('property.property', string="Property")
    allocation_status = fields.Char(string="Allocation Status")
    parking_id = fields.Many2one('product.template', string="Parking")

