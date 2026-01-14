# -- encoding: utf-8 --
##############################################################################
#
#    Cloud Science Labs
#    Copyright (C) 2024 (https://www.cloudsciencelabs.com/)
#
##############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Property(models.Model):
    """A class for the model property to represent the property"""

    _name = "property.property"
    _description = "Property"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Name", required=True, copy=False, help="Name of the Property"
    )
    code = fields.Char(
        string="Reference",
        readonly=True,
        copy=False,
        default=lambda self: _("New"),
        help="Sequence/code for the property",
    )
    property_type = fields.Selection(
        [
            ("residential", "Residential"),
            ("commercial", "Commercial"),
            ("industry", "Residential & Commercial"),
        ],
        string="Type",
        help="The type of the property",
        default="industry"
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("available", "Active"),
            ("rented", "Rented"),
            ("sold", "Sold"),
        ],
        required=True,
        string="Status",
        default="draft",
        help="* The 'Draft' status is used when the property is in draft.\n"
        "* The 'Available' status is used when the property is "
        "available or confirmed\n"
        "* The 'Rented' status is used when the property is rented.\n"
        "* The 'sold' status is used when the property is sold.\n",
    )
    street = fields.Char(string="Street", required=True, help="The street name")
    street2 = fields.Char(string="Street2", help="The street2 name")
    zip = fields.Char(string="Zip", change_default=True, help="Zip code for the place")
    city = fields.Char(string="City", help="The name of the city")
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        ondelete="restrict",
        required=True,
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
    latitude = fields.Float(
        string="Latitude",
        digits=(16, 5),
        help="The latitude of where the property is " "situated",
    )
    longitude = fields.Float(
        string="Longitude",
        digits=(16, 5),
        help="The longitude of where the property is " "situated",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Property Management Company",
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        "res.currency", string="Currency", related="company_id.currency_id"
    )
    image = fields.Binary(string="Image", help="Image of the property")
    construct_year = fields.Char(
        string="Construct Year", size=4, help="Year of construction of the property"
    )
    license_no = fields.Char(
        string="License No.", help="License number of the property"
    )
    landlord_id = fields.Many2one(
        "res.partner", string="LandLord", help="The owner of the property"
    )
    description = fields.Text(
        string="Description", help="A brief description about the property"
    )
    responsible_id = fields.Many2one(
        "res.users",
        string="Responsible Person",
        help="The responsible person for " "this property",
        default=lambda self: self.env.user,
    )
    type_residence = fields.Char(
        string="Type of Residence", help="The type of the residence"
    )
    total_floor = fields.Integer(
        string="Total Floor",
        default=1,
        help="The total number of floor in " "the property",
    )
    bedroom = fields.Integer(
        string="Bedrooms", help="Number of bedrooms in the property"
    )
    bathroom = fields.Integer(
        string="Bathrooms", help="Number of bathrooms in the property"
    )
    parking = fields.Integer(
        string="Parking",
        help="Number of cars or bikes that can be parked " "in the property",
    )
    furnishing = fields.Selection(
        [
            ("no_furnished", "Not Furnished"),
            ("half_furnished", "Partially Furnished"),
            ("furnished", "Fully Furnished"),
        ],
        string="Furnishing",
        help="Whether the residence is fully furnished or partially/half "
        "furnished or not at all furnished",
    )
    land_name = fields.Char(string="Land Name", help="The name of the land")
    land_area = fields.Char(
        string="Area In Hector", help="The area of the land in hector"
    )
    shop_name = fields.Char(string="Shop Name", help="The name of the shop")
    industry_name = fields.Char(string="Industry Name", help="The name of the industry")
    usage = fields.Char(
        string="Used For", help="For what purpose is this property used for"
    )
    location = fields.Char(string="Location", help="The location of the property")
    property_image_ids = fields.One2many(
        "property.image", "property_id", string="Property Images"
    )
    area_measurement_ids = fields.One2many(
        "property.area.measure", "property_id", string="Area Measurement"
    )
    total_sq_feet = fields.Float(
        string="Total Square Feet",
        compute="_compute_total_sq_feet",
        help="The total area square feet of the " "property",
    )
    facility_ids = fields.Many2many(
        "property.facility", string="Facilities", help="Facilities of the property"
    )
    nearby_connectivity_ids = fields.One2many(
        "property.nearby.connectivity", "property_id", string="Nearby Connectives"
    )
    property_tags = fields.Many2many(
        "property.tag", string="Property Tags", help="Tags for the property"
    )
    attachment_id = fields.Many2one("ir.attachment", string="Attachment")
    sale_rent = fields.Selection(
        [
            ("for_sale", "For Sale"),
            ("for_tenancy", "For Tenancy"),
            ("for_auction", "For Auction"),
        ],
        string="Sale | Rent",
        required=True,
    )
    unit_price = fields.Monetary(
        string="Sales Price", help="Selling price of the Property."
    )
    sale_id = fields.Many2one(
        "property.sale",
        string="Sale Order",
        help="The corresponding property sale",
        tracking=True,
    )
    rent_month = fields.Monetary(
        string="Rent/Month", help="Rent price per month", tracking=True
    )
    is_installment_payment = fields.Boolean(
        string="Installment Payment", help="Payments are made in installment"
    )
    monthly_or_yearly = fields.Selection([('monthly', 'Monthly'),
                                  ('yearly', 'Yearly')],
                                 string="Monthly / Yearly",
                                 help="Automatically selects the Contract Period",
                                 tracking=True)
    no_of_months = fields.Integer(string="Number of Months")
    no_of_years = fields.Integer(string="Number of Years")
    no_of_installments = fields.Integer(string="Number of Installments", compute='_compute_installments', store=True)
    amount_per_installment = fields.Float(string="Amount Per Installment", compute='_compute_installments', store=True)
    property_units_ids = fields.One2many('property.units.link', 'property_id', string="Property Floor's")
    project_id = fields.Many2one('project.project', string="Property Project")

    @api.model
    def create(self, vals):
        """Generating sequence number at the time of creation of record"""
        if vals.get("code", "New") == "New":
            vals["code"] = (
                self.env["ir.sequence"].next_by_code("property.property") or "New"
            )
        res = super(Property, self).create(vals)
        return res

    def _compute_total_sq_feet(self):
        """Calculates the total square feet of the property"""
        for rec in self:
            rec.total_sq_feet = sum(rec.mapped("area_measurement_ids").mapped("area"))

    @api.model
    def _geo_localize(self, street="", zip="", city="", state="", country=""):
        """Generate Latitude and Longitude based on address"""
        geo_obj = self.env["base.geocoder"]
        search = geo_obj.geo_query_address(
            street=street, zip=zip, city=city, state=state, country=country
        )
        result = geo_obj.geo_find(search, force_country=country)
        if result is None:
            search = geo_obj.geo_query_address(city=city, state=state, country=country)
            result = geo_obj.geo_find(search, force_country=country)
        return result

    @api.onchange("street", "zip", "city", "state_id", "country_id")
    def _onchange_address(self):
        """Writing Latitude and Longitude to the record"""
        for rec in self.with_context(lang="en_US"):
            result = rec._geo_localize(
                rec.street, rec.zip, rec.city, rec.state_id.name, rec.country_id.name
            )
            if result:
                rec.write(
                    {
                        "latitude": result[0],
                        "longitude": result[1],
                    }
                )

    def action_get_map(self):
        """Redirects to google map to show location based on latitude
        and longitude"""
        return {
            "type": "ir.actions.act_url",
            "name": "View Map",
            "target": "self",
            "url": "/map/%s/%s" % (self.latitude, self.longitude),
        }

    def action_available(self):
        """Set the state to available"""
        self.state = "available"

    def action_property_sale_view(self):
        """View Sale order Of the Property"""
        return {
            "name": "Property Sale: " + self.code,
            "view_mode": "list,form",
            "res_model": "property.sale",
            "type": "ir.actions.act_window",
            "res_id": self.sale_id.id,
        }

    def action_property_rental_view(self):
        """View rental order Of the Property"""
        return {
            "name": "Property Rental: " + self.code,
            "view_mode": "list,form",
            "res_model": "property.rental",
            "type": "ir.actions.act_window",
            "domain": [("property_id", "=", self.id)],
        }
    
    @api.depends('unit_price', 'no_of_months', 'no_of_years')
    def _compute_installments(self):
        for record in self:
            if record.no_of_months or record.no_of_years:
                record.no_of_installments = record.no_of_months or record.no_of_years
                if record.unit_price:
                    record.amount_per_installment = record.unit_price / record.no_of_installments
            else:
                record.no_of_installments = 0
                record.amount_per_installment = 0.00

    def create_floor(self):
        if not len(self.property_units_ids) > 0:
            dic = {}
            floor_obj = self.env['property.floor']
            unit_obj = self.env['property.units.link']
            for record in range(self.total_floor + 1)[1:]:
                floor = floor_obj.sudo().create({'property_id': self.id, 'name': 'Floor' + str(record),}),
                dic = {
                        'floor': floor[0].id,
                        'property_id': self.id,
                }
                unit_obj.sudo().create(dic)

    def create_unit(self):
        dic = {}
        unit_obj = self.env['product.template']
        for record in self.mapped('property_units_ids'):
            if len(record.unit_id) <= 0:
                lst = []
                for unit in range(record.number_of_units + 1)[1:]:
                    dic = {
                            'name': 'Unit'+ str(unit),
                            'type': 'product',
                            'property_name': self.id,
                            'property_type': record.property_type,
                            'active_status': True,
                            'current_vacancy': True,
                            'use_unit_utilities': True,
                            'floor': record.floor.id,
                    }
                    u = unit_obj.sudo().create(dic)
                    lst.append(u.id)
                record.unit_id = [(6, 0, lst)]

    def link_unit(self):
        dic = {}
        unit_obj = self.env['product.template']
        for record in self.mapped('property_units_ids'):
            lst = []
            units = unit_obj.search([('property_name', '=', self.id), 
                                     ('floor', '=', record.floor.id)])
            for rec in units:
                lst.append(rec.id)
            record.unit_id = [(6, 0, lst)]

        # for record in self.mapped('property_units_ids'):
        #     if len(record.unit_id) <= 0:
        #         lst = []
        #         for unit in range(record.number_of_units + 1)[1:]:
        #             dic = {
        #                     'name': 'Unit'+ str(unit),
        #                     'type': 'product',
        #                     'property_name': self.id,
        #                     'property_type': record.property_type,
        #                     'active_status': True,
        #                     'current_vacancy': True,
        #                     'use_unit_utilities': True,
        #                     'floor': record.floor.id,
        #             }
        #             u = unit_obj.sudo().create(dic)
        #             lst.append(u.id)
        #         record.unit_id = [(6, 0, lst)]

    def action_property_units_view(self):
        unit_obj = self.env['product.template']
        action = self.env.ref('product.product_template_action').read()[0]
        lst = []
        for unit_ob in unit_obj.search([('property_name', '=', self.id)]):
            lst.append(unit_ob.id)
        if len(lst) > 1:
            action['domain'] = [('id', 'in', lst)]
        elif len(lst) == 1:
            action['views'] = [(self.env.ref('product.product_template_only_form_view').id, 'form')]
            action['res_id'] = lst[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


class PropertyUnits_link(models.Model):
    """A class for the model property to represent the property"""
    _name = "property.units.link"
    _description = "Property Units"

    floor = fields.Many2one('property.floor', string="Floor")
    description = fields.Char(string="Description")
    property_id = fields.Many2one('property.property', string="Property")
    property_type = fields.Selection(
        [
            ("residential", "Residential"),
            ("commercial", "Commercial"),
        ],
        string="Type",
        help="The type of the property",
    )
    number_of_units = fields.Integer(string="Number of Units")
    unit_id = fields.Many2many('product.template', string="Unit's")
    square_feet = fields.Integer(string="Square Feet")
    unit_id_create = fields.Many2one('product.template', string="Create Units")
    street = fields.Char(related='property_id.street')
    street2 = fields.Char(related='property_id.street2')
    zip = fields.Char(related='property_id.zip')
    city = fields.Char(related='property_id.city')
    country_id = fields.Many2one('res.country', string="Country", related='property_id.country_id')
    state_id = fields.Many2one('res.country.state', string="State", related='property_id.state_id')

    def unit_create(self):
        if not self.property_type:
            raise ValidationError(
                _('Please provide the property type and Square feet in  %r.', self.floor.name))
        view_id = self.env.ref('product.product_template_only_form_view').id
        context = dict(self.env.context)
        city = context.get('default_city')
        street = context.get('default_street')
        active_status = context.get('active_status')
        square_feet = context.get('square_feet')
        context.update({
            'default_street': street,
            'property_name': self.id,
            'default_floor': self.floor.id,
            'default_active_status': active_status,
            'default_property_type': self.property_type,
            'default_check_readonly': True,
        })
        self.env.context = context
        return {
            'name':'Units',
            'view_type':'form',
            'view_mode':'list',
            'views' : [(view_id,'form')],
            'res_model':'product.template',
            'view_id':view_id,
            'type':'ir.actions.act_window',
            'target':'new',
            'context': context,
        }


class Floor(models.Model):
    _name = "property.floor"
    _description = "Property Floor"

    name = fields.Char()
    property_id = fields.Many2one('property.property', string="Property")
    property_type = fields.Selection(
        [
            ("residential", "Residential"),
            ("commercial", "Commercial"),
            # ("industry", "Residential & Commercial"),
        ],
        string="Type",
        help="The type of the property",
    )


class Project_Property(models.Model):
    _inherit = 'project.project'
    _description = 'Project Property'

    property_ids = fields.One2many('property.property', 'project_id', string="Property")

    property_image = fields.Binary('property_image')
    project_number = fields.Integer(string="Project Number")
    email_address = fields.Char(string="Email Address")
    description = fields.Html(string="Description")
    number_of_building = fields.Integer(string="Number Of Building")
    status = fields.Char(string="Status")
    rera_number = fields.Char(string="Rera Number")

    project_address = fields.Char(string="Project Address")
    office_location = fields.Char(string="Office Location")
    city = fields.Char(string="City")
    po_box = fields.Char(string="P.O Box")

    contractor = fields.Char(string="Contractor")
    seller_name = fields.Char(string="Seller Name")
    project_developer_name = fields.Char(string="Project Developer Name")

    amenties = fields.Char(string="Amenties")
    Video = fields.Html(string="Video")


