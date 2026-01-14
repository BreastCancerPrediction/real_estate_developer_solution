# -- encoding: utf-8 --
##############################################################################
#
#    Cloud Science Labs
#    Copyright (C) 2024 (https://www.cloudsciencelabs.com/)
#
##############################################################################
import werkzeug.utils
from odoo import fields, http
from odoo.http import request
from werkzeug.wrappers import Response


class PropertyController(http.Controller):
    """A controller class that shows the related functions to the property"""

    @http.route('/property', auth='public', website=True)
    def property(self, **kwargs):
        # Get filter values from query params
        project_id = kwargs.get('project_id')
        country_id = kwargs.get('country_id')
        construct_year = kwargs.get('construct_year')
        state_id = kwargs.get('state_id')
        city = kwargs.get('city')

        domain = []

        if project_id:
            domain.append(('project_id', '=', int(project_id)))
        if country_id:
            domain.append(('country_id.id', '=', int(country_id)))
        if construct_year:
            domain.append(('construct_year', '=', construct_year))
        if state_id:
            domain.append(('state_id.id', '=', int(state_id)))
        if city:
            domain.append(('city', '=', city))

        properties = request.env['property.property'].sudo().search(domain)
        all_construct_years = request.env['property.property'].sudo().search([]).mapped('construct_year')
        construct_years = sorted(set(filter(None, all_construct_years)))
        all_city_names = request.env['property.property'].sudo().search([]).mapped('city')
        city_names = list(set(filter(None, all_city_names)))
        used_states = request.env['property.property'].sudo().search([]).mapped('state_id')
        unique_states = request.env['res.country.state'].browse(list(set(used_states.ids)))

        if country_id:
            states = request.env['res.country.state'].sudo().search([('country_id', '=', int(country_id))])
        else:
            states = request.env['res.country.state'].sudo().search([])
        values = {
            'property_ids': properties,
            'projects': request.env['project.project'].sudo().search([]),
            'countries': request.env['res.country'].sudo().search([]),
            'states': states,
            'construct_years': construct_years,
            'city_names': city_names,
            'selected_project_id': int(project_id) if project_id else '',
            'selected_country_id': int(country_id) if country_id else '',
            'selected_state_id': int(state_id) if state_id else '',
            'selected_construct_year': construct_year or '',
            'selected_city': city or '',
        }
        return request.render('real_estate_management.property_view', values)

    @http.route('/property/<int:property_id>', auth='public', website=True)
    def property_item(self, property_id):
        """ Shows each corresponding properties view in property_view_item """
        return request.render('real_estate_management.property_view_item',
                              {
                                  'property_id': request.env[
                                      'property.property'].sudo().browse(
                                      property_id),
                              })

    @http.route('/map/<latitude>/<longitude>', type='http', auth='public')
    def redirect_map(self, latitude, longitude):
        """ Returns the Google map location for the corresponding latitude
        and longitude """
        return werkzeug.utils.redirect(
            "https://www.google.com/maps/@%s,%s,115m/data=!3m1!1e3" % (
                latitude, longitude))

    @http.route('/property/auction/', type='json', auth='public')
    def auction(self):
        """Returns properties in three different states"""
        auction_ids = request.env['property.auction'].sudo().search([
            ('state', '!=', 'draft')
        ])
        context = {
            'confirmed': [],
            'started': [],
            'ended': [],
        }
        for auction_id in auction_ids:
            participants = sorted(auction_id.participant_ids,
                                  key=lambda x: x.bid_amount, reverse=True)
            data = {
                'id': auction_id.id,
                'name': auction_id.property_id.name,
                'code': auction_id.auction_seq,
                'image': auction_id.property_id.image,
                'start': auction_id.start_time,
                'start_price': auction_id.bid_start_price,
                'last': participants[0].bid_amount if participants else 0,
                'end': auction_id.end_time,
                'winner': auction_id.auction_winner_id.name,
                'final_rate': auction_id.final_price,
                'total_participant': len(auction_id.participant_ids.ids)
            }
            if auction_id.state == 'confirmed':
                context['confirmed'].append(data)
            elif auction_id.state == 'started':
                context['started'].append(data)
            elif auction_id.state == 'ended':
                context['ended'].append(data)
        response = http.Response(
            template='real_estate_management.auction_view',
            qcontext=context)
        return response.render()

    @http.route('/property/auction/<int:prop_id>/bid', type='json',
                auth='public')
    def auction_bid_submit(self, prop_id, **kw):
        """Return success when auction is submitted"""
        auction_id = request.env['property.auction'].sudo().browse(int(prop_id))
        auction_id.write({
            'participant_ids': [
                fields.Command.create({
                    'partner_id': request.env.user.partner_id.id,
                    'bid_time': fields.Datetime.now(),
                    'bid_amount': float(kw.get('bid_amount'))
                })
            ]
        })
        return {'message': 'success'}

    @http.route('/units', auth='public', website=True) 
    def units(self, **kwargs):
        domain = [('is_unit', '=', True)]
        price = kwargs.get('price')
        if price and price != 'all':
            if '-' in price:
                min_price, max_price = map(int, price.split('-'))
                domain.append(('unit_price', '>=', min_price))
                domain.append(('unit_price', '<=', max_price))
            else:
                domain.append(('unit_price', '>=', int(price)))

        # Property filter by ID
        property_id = kwargs.get('property_id')
        if property_id:
            domain.append(('property_name', '=', int(property_id)))

        # Property filter by ID
        floor_id = kwargs.get('floor_id')
        country_id = kwargs.get('country_id')
        state_id = kwargs.get('state_id')
        city = kwargs.get('city')
        if floor_id:
            domain.append(('floor', '=', int(floor_id)))

        if kwargs.get('property_type'):
           domain.append(('property_type','=',kwargs['property_type']))

        if kwargs.get('unit_type_filter'):
           domain.append(('unit_category','=',kwargs['unit_type_filter']))
           
        # City filter
        if kwargs.get('city'):
            domain.append(('city', '=', kwargs['city']))
        if country_id:
            domain.append(('country_id.id', '=', int(country_id)))

        if kwargs.get('property_type'):
            domain.append(('property_type', '=', kwargs['property_type']))
        if kwargs.get('unit_category'):
            domain.append(('unit_category', '=', kwargs['unit_category']))
        if kwargs.get('number_of_bedroom'):
            unit_type = request.env['unit.type'].sudo().search([
                ('name', 'ilike', kwargs['number_of_bedroom'])
            ], limit=1)
            if unit_type:
                domain.append(('unit_type_id', '=', unit_type.id))
        if kwargs.get('property_status'):
            domain.append(('property_status', '=', kwargs['property_status']))
        if kwargs.get('possession'):
            domain.append(('possession', '=', kwargs['possession']))
        if kwargs.get('min_price'): 
            domain.append(('unit_price', '>=', int(kwargs['min_price'])))
        if kwargs.get('max_price'): 
            domain.append(('unit_price', '<=', int(kwargs['max_price'])))
        if kwargs.get('city'):
           domain.append(('city', '=', kwargs['city']))
        if state_id:
            domain.append(('state_id.id', '=', int(state_id)))
        if country_id:
            domain.append(('country_id.id', '=', int(country_id)))
        if country_id:
            states = request.env['res.country.state'].sudo().search([('country_id', '=', int(country_id))])
        else:
            states = request.env['res.country.state'].sudo().search([])
        all_city_names = request.env['property.property'].sudo().search([]).mapped('city')
        city_names = list(set(filter(None, all_city_names)))
        units = request.env['product.template'].sudo().search(domain)
        properties = request.env['property.property'].sudo().search([])
        floors = []
        if property_id:
            property_rec = request.env['property.property'].sudo().browse(int(property_id))
            floors = sorted(
                list({link.floor for link in property_rec.property_units_ids if link.floor}),
                key=lambda f: f.name
            )
        return request.render('real_estate_management.unit_view', {
            'units_ids': units,
            'properties':properties,
            'selected_filters': kwargs,
            'floors':floors,
            'city_names':city_names,
            'states':states,
            'selected_country_id': int(country_id) if country_id else '',
            'selected_state_id': int(state_id) if state_id else '',
            'selected_city': city or '',
            'countries': request.env['res.country'].sudo().search([]),
        })

    @http.route('/units/<int:property_id>', auth='public', website=True)
    def units_item(self, property_id):
        property_obj = request.env['property.property'].sudo().browse(property_id)
        """ Shows each corresponding properties view in property_view_item """
        return request.render('real_estate_management.unit_view',
                              {
                                  'units_ids': request.env[
                                      'product.template'].sudo().search([('property_name', '=', property_obj.id)]
                                      ),
                              })

    @http.route('/projects', auth='public', website=True)
    def projects(self, **kwargs):
        projects = request.env['project.project'].sudo().search([])
        return request.render('real_estate_management.projects_view', {
            'projects': projects,
        })

    @http.route('/properties/<int:project_id>',auth='public', website=True)
    def get_properties_by_project(self, project_id):
        properties = request.env['property.property'].sudo().search([
            ('project_id', '=', int(project_id))
        ])
        return request.render('real_estate_management.property_view',{
            'property_ids':properties
        })


    @http.route('/create_crm_lead', type='http', auth='public', methods=['POST'], csrf=False, website=True)
    def create_crm_lead(self, **post):
        name = post.get('name')
        email = post.get('email')
        phone = post.get('phone')
        message = post.get('message')
        unit_id = post.get('unit_id')

        if not name or not unit_id:
            return Response("Missing required fields", status=400, content_type='text/plain')

        # Proceed to create CRM lead
        unit = request.env['product.template'].sudo().browse(int(unit_id))

        lead = request.env['crm.lead'].sudo().create({
            'name': f"Inquiry from {name} for property unit {unit.name}",
            'contact_name': name,
            'email_from': email,
            'phone': phone,
            'description': f"Message: {message}",
        })
        # Optional: Send confirmation email
        if email:
            template = request.env.ref('real_estate_management.email_template_unit_inquiry', raise_if_not_found=False)
            if template:
                template.sudo().send_mail(lead.id, force_send=True)

        return request.redirect('/thank-you')

    @http.route('/thank-you', type='http', auth='public', website=True)
    def thank_you(self, **kw):
        return request.render('real_estate_management.thank_you_template')