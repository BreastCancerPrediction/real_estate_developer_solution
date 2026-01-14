from datetime import timedelta

from odoo import SUPERUSER_ID, api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import is_html_empty
import base64


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('sale_order_template_id')
    def _onchange_sale_order_template_id(self):
        sale_order_template = self.sale_order_template_id.with_context(lang=self.partner_id.lang)
        order_lines_data = [fields.Command.clear()]
        order_lines_data += [
            fields.Command.create(line._prepare_order_line_values())
            for line in sale_order_template.sale_order_template_line_ids
        ]
        if len(order_lines_data) >= 2:
            order_lines_data[1][2]['sequence'] = -99

        for lead in self.env['crm.lead'].browse(self._context.get('active_id')):
            for prop in lead.property_ids:
                if prop.assigned_unit:
                    order_lines_data.append(
                        fields.Command.create({
                            'product_id': self.env['product.product'].search([('product_tmpl_id', '=', prop.assigned_unit.id)],limit=1).id,
                            'product_template_id': prop.assigned_unit.id,
                            'name': prop.assigned_unit.name,
                            'product_uom_qty': 1,
                        })
                    )

        self.order_line = order_lines_data
        option_lines_data = [fields.Command.clear()]
        option_lines_data += [
            fields.Command.create(option._prepare_option_line_values())
            for option in sale_order_template.sale_order_template_option_ids
        ]
        self.sale_order_option_ids = option_lines_data


    # send attachment of unit in send by email wizard
    def action_quotation_send(self):
        res = super().action_quotation_send()

        for order in self:
            if order.order_line and order.order_line[0].product_id.product_tmpl_id:
                template = order.order_line[0].product_id.product_tmpl_id

                # Custom report XML ID for product template brochure
                report_xml_id = 'real_estate_management.action_product_template_report'

                report = self.env.ref(report_xml_id, raise_if_not_found=True)
                pdf_content = self.env['ir.actions.report']._render_qweb_pdf(report.xml_id, [template.id])[0]

                attachment = self.env['ir.attachment'].create({
                    'name': f'Unit Brochure - {template.name}.pdf',
                    'type': 'binary',
                    'datas': base64.b64encode(pdf_content),
                    'res_model': 'sale.order',
                    'res_id': order.id,
                    'mimetype': 'application/pdf',
                })

                # Now add both attachments (existing Sale Order report + your new attachment)
                if 'context' not in res or not isinstance(res['context'], dict):
                    res['context'] = {}

                res['context'] = dict(res['context'])
                attachment_ids = res['context'].get('default_attachment_ids', [])

                # Attach custom brochure
                attachment_ids.append((4, attachment.id))

                # Attach default sale order report PDF (usually automatically attached, but let's ensure it)
                sale_order_report = self.env.ref('sale.action_report_saleorder', raise_if_not_found=False)
                if sale_order_report:
                    sale_order_pdf = \
                    self.env['ir.actions.report']._render_qweb_pdf(sale_order_report.report_name, [order.id])[0]
                    sale_order_attachment = self.env['ir.attachment'].create({
                        'name': f'Sale Order - {order.name}.pdf',
                        'type': 'binary',
                        'datas': base64.b64encode(sale_order_pdf),
                        'res_model': 'sale.order',
                        'res_id': order.id,
                        'mimetype': 'application/pdf',
                    })
                    attachment_ids.append((4, sale_order_attachment.id))

                unit = order.order_line[0].product_id.product_tmpl_id
                quotation_number = order.name or ''
                unit_name = unit.name or ''
                floor_name = unit.floor_id.name if unit.floor_id else ''
                property_name = unit.property_name.name if unit.property_name else ''
                unit_location = f"{floor_name}, {property_name}".strip(', ')
                phone = order.company_id.phone or ''

                res['context']['default_attachment_ids'] = attachment_ids
                res['context'][
                    'default_body'] = f"""
<p>Dear Customer,<br/><br/>
We are pleased to provide you with the official quotation for your interest in a unit within our prestigious <strong>{property_name}</strong> project.<br/><br/>
Attached to this email, you will find the detailed quotation (Quotation No: {quotation_number}), which outlines the pricing, payment terms, and other relevant details for Unit <strong>{unit_name}</strong> located at <strong>{unit_location}</strong>.<br/><br/>
We believe this unit offers an excellent opportunity and aligns perfectly with your requirements.<br/><br/>
Please take your time to review the attached document. Should you have any questions, require further clarification, or wish to discuss any aspect of the quotation, please do not hesitate to reply to this email or contact us directly at {phone}.<br/><br/>
We look forward to the possibility of welcoming you to the {property_name} community.<br/><br/>
Thank you for your continued interest.<br/><br/>
Regards,<br/>{order.company_id.name}</p>
"""

        return res

