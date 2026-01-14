# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Bhagyadev KP (odoo@cybrosys.com)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
################################################################################
from ast import literal_eval
from odoo import api, fields, models
from odoo.osv import expression


class DashboardBlock(models.Model):
    """Class is used to create charts and tiles in dashboard"""
    _name = "dashboard.block"
    _description = "Dashboard Block"

    def get_default_action(self):
        """Function to get values from dashboard if action_id is true return
        id else return false"""
        action_id = self.env.ref(
            'odoo_dynamic_dashboard.dashboard_view_action')
        if action_id:
            return action_id.id
        return False

    name = fields.Char(string="Name", help='Name of the block')
    fa_icon = fields.Char(string="Icon", help="Add icon for tile")
    operation = fields.Selection(
        selection=[("sum", "Sum"), ("avg", "Average"), ("count", "Count")],
        string="Operation",
        help='Tile Operation that needs to bring values for tile',
        required=True)
    graph_type = fields.Selection(
        selection=[("bar", "Bar"), ("radar", "Radar"), ("pie", "Pie"),
                   ("polarArea", "polarArea"), ("line", "Line"),
                   ("doughnut", "Doughnut")],
        string="Chart Type", help='Type of Chart')
    measured_field_id = fields.Many2one("ir.model.fields",
                                        string="Measured Field",
                                        help="Select the Measured")
    client_action_id = fields.Many2one('ir.actions.client',
                                       string="Client action",
                                       default=get_default_action,
                                       help="Client action")
    type = fields.Selection(
        selection=[("graph", "Chart"), ("tile", "Tile"),("table","Table")],
        string="Type", help='Type of Block ie, Chart or Tile')
    x_axis = fields.Char(string="X-Axis", help="Chart X-axis")
    y_axis = fields.Char(string="Y-Axis", help="Chart Y-axis")
    height = fields.Char(string="Height ", help="Height of the block")
    width = fields.Char(string="Width", help="Width of the block")
    translate_x = fields.Char(string="Translate_X",
                              help="x value for the style transform translate")
    translate_y = fields.Char(string="Translate_Y",
                              help="y value for the style transform translate")
    data_x = fields.Char(string="Data_X", help="Data x value for resize")
    data_y = fields.Char(string="Data_Y", help="Data y value for resize")
    group_by_id = fields.Many2one("ir.model.fields",
                                  string="Group by(Y-Axis)",
                                  help='Field value for Y-Axis')
    tile_color = fields.Char(string="Tile Color", help='Primary Color of Tile')
    text_color = fields.Char(string="Text Color", help='Text Color of Tile')
    val_color = fields.Char(string="Value Color", help='Value Color of Tile')
    fa_color = fields.Char(string="Icon Color", help='Icon Color of Tile')
    filter = fields.Char(string="Filter", help="Add filter")
    model_id = fields.Many2one('ir.model', string='Model',
                               help="Select the module name")
    model_name = fields.Char(related='model_id.model', string="Model Name",
                             help="Added model_id model")
    field_ids = fields.Many2many(
        'ir.model.fields',
        string="Fields",
        domain="[('model_id', '=', model_id)]",
        help="Select the fields to display in the table."
    )
    edit_mode = fields.Boolean(string="Edit Mode",
                               help="Enable to edit chart and tile",)
                            

    @api.onchange('model_id')
    def _onchange_model_id(self):
        if self.operation or self.measured_field_id:
            self.operation = False
            self.measured_field_id = False

    def get_dashboard_vals(self, action_id, start_date=None, end_date=None):
        """Fetch block values from js and create chart"""
        block_id = []
        for rec in self.env['dashboard.block'].sudo().search(
                [('client_action_id', '=', int(action_id))]):
            if rec.filter is False:
                rec.filter = "[]"
            filter_list = literal_eval(rec.filter)
            filter_list = [filter_item for filter_item in filter_list if not (
                    isinstance(filter_item, tuple) and filter_item[
                0] == 'create_date')]
            rec.filter = repr(filter_list)
            vals = {'id': rec.id, 'name': rec.name, 'type': rec.type,
                    'graph_type': rec.graph_type, 'icon': rec.fa_icon,
                    'model_name': rec.model_name,
                    'color': f'background-color: {rec.tile_color};' if rec.tile_color else '#1f6abb;',
                    'text_color': f'color: {rec.text_color};' if rec.text_color else '#FFFFFF;',
                    'val_color': f'color: {rec.val_color};' if rec.val_color else '#FFFFFF;',
                    'icon_color': f'color: {rec.tile_color};' if rec.tile_color else '#1f6abb;',
                    'height': rec.height,
                    'width': rec.width,
                    'translate_x': rec.translate_x,
                    'translate_y': rec.translate_y,
                    'data_x': rec.data_x,
                    'data_y': rec.data_y,
                    'domain': filter_list,
                    }
            domain = []
            if rec.filter:
                domain = expression.AND([literal_eval(rec.filter)])
            if rec.model_name:
                if rec.type == 'graph':
                    self._cr.execute(self.env[rec.model_name].get_query(domain,
                                                                        rec.operation,
                                                                        rec.measured_field_id,
                                                                        start_date,
                                                                        end_date,
                                                                        group_by=rec.group_by_id))
                    records = self._cr.dictfetchall()
                    x_axis = []
                    for record in records:
                        if record.get('name') and type(
                                record.get('name')) == dict:
                            x_axis.append(record.get('name')[self._context.get(
                                'lang') or 'en_US'])
                        else:
                            x_axis.append(record.get(rec.group_by_id.name))
                    y_axis = []
                    for record in records:
                        y_axis.append(record.get('value'))
                    vals.update({'x_axis': x_axis, 'y_axis': y_axis})
                elif rec.type == 'tile':
                    self._cr.execute(self.env[rec.model_name].get_query(domain,
                                                                        rec.operation,
                                                                        rec.measured_field_id,
                                                                        start_date,
                                                                        end_date))
                    records = self._cr.dictfetchall()
                    magnitude = 0
                    total = records[0].get('value')
                    while abs(total) >= 1000:
                        magnitude += 1
                        total /= 1000.0
                    val = '%.2f%s' % (
                        total, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
                    records[0]['value'] = val
                    vals.update(records[0])


                elif rec.type == 'table':
                    if not rec.field_ids:
                        vals.update({
                            'columns': [],
                            'records': [],
                        })
                    else:
                        # Get the selected fields in the same order as field_ids
                        selected_fields = rec.field_ids.mapped('name')
                        columns = [{'name': field.field_description, 'technical_name': field.name} for field in rec.field_ids]
                        
                        # Validate fields against the model's fields
                        model_fields = self.env[rec.model_name]._fields.keys()
                        valid_fields = [field for field in selected_fields if field in model_fields]
                        invalid_fields = set(selected_fields) - set(valid_fields)
                        if invalid_fields:
                            print(f"Invalid fields detected in selected_fields: {invalid_fields}")
                                # Add date range filtering
                        if start_date and end_date:
                            date_filter = [('create_date', '>=', start_date), ('create_date', '<=', end_date)]
                            domain = domain or []  # Initialize domain if not already done
                            domain = expression.AND([domain, date_filter])
                            # domain = expression.AND([literal_eval(rec.filter)])
                        records = []
                        if valid_fields:
                            try:
                                # Fetch records while preserving the selected field order
                                records = self.env[rec.model_name].search_read(domain, valid_fields)
                            except Exception as e:
                                print(f"Error fetching records for model {rec.model_name}: {str(e)}")
                        formatted_records = []
                        for record in records:
                            formatted_record = {}
                            for field in valid_fields:
                                value = record.get(field)

                                if isinstance(value, dict) and 'id' in value:
                                    formatted_record[field] = value.get('id')  # Relational field as dict
                                elif isinstance(value, (list, tuple)) and all(isinstance(v, dict) for v in value):
                                    formatted_record[field] = [v.get('id') for v in value]  # Many2many field
                                elif hasattr(value, 'id'):
                                    formatted_record[field] = value.id  # Single relational object
                                else:
                                    formatted_record[field] = value  # Normal field or None

                            formatted_records.append(formatted_record)

                        # Update the result dictionary
                        vals.update({
                            'columns': columns,
                            'records': formatted_records,
                        })
            block_id.append(vals)
        return block_id


    def get_save_layout(self, grid_data_list):
        """Function to fetch edited values while editing the layout of the chart or tile
        and save values in the database."""
        for data in grid_data_list:
            block = self.browse(int(data['id']))
            
            # Prepare data for write operation
            values = {}

            # Handle translation (x, y) updates
            if 'data-x' in data and 'data-y' in data:
                values.update({
                    'translate_x': f"{data['data-x']}px",
                    'translate_y': f"{data['data-y']}px",
                    'data_x': data.get('data-x', '0'),
                    'data_y': data.get('data-y', '0'),
                })

            # Handle dimensions (height, width) updates
            if 'height' in data and 'width' in data:
                values.update({
                    'height': f"{data['height']}px",
                    'width': f"{data['width']}px",
                })

            # Write only if there are changes to apply
            if values:
                block.write(values)

        return True
