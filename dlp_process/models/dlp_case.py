# -- encoding: utf-8 --
##############################################################################
#
#    Cloud Science Labs (https://www.cloudsciencelabs.com/)
#
##############################################################################
from odoo import models, fields, api, _


class DlpCase(models.Model):
    _name = 'dlp.case'
    _description = 'DLP Case'
    _rec_name = 'seq_num'

    status = fields.Selection([('new','New'), ('closed','Closed')], string="Status", default="new")
    seq_num = fields.Char(string='Case Number', readonly=True, copy=False, index=True,default=lambda self: _('New'))
    case_record_type = fields.Selection([('defect_liability_complaint','Defect Liability Complaint'),('other', 'Other')],string="Case Record Type",default='defect_liability_complaint')
    case_origin = fields.Char(string="Case Origin")
    work_order_status = fields.Char(string="Work Order Status")
    work_order_incident_description = fields.Char(string="Work Order Incident Description")
    work_order_closure_reason = fields.Char(string="Work Order Closure Reason")
    work_order_account = fields.Many2one('res.partner',string="Work Order Account")
    work_order_subject = fields.Char(string="Work Order Subject")
    wo_type_of_incident = fields.Char(string="Work Order Type Of Incident")
    wo_resolution_priority = fields.Selection([('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')],string="Work Order Resolution Priority")
    wo_resolution_typology = fields.Selection([('repair', 'Repair'),('replacement', 'Replacement'),
        ('refund', 'Refund'),('maintenance', 'Maintenance'),('other', 'Other')], string="Work Order Resolution Typology")
    wo_category = fields.Char(string="Work Order Category")
    wo_sub_category = fields.Char(string="Work Order Sub Category")
    wo_location = fields.Selection([('master_bedroom', 'Master Bedroom'),
        ('maids_bedroom', 'Maids Bedroom'),('kitchen', 'Kitchen'),
        ('living_room', 'Living Room'),('bathroom', 'Bathroom'),
        ('balcony', 'Balcony')],string="Work Order Location")
    wo_currency_code = fields.Char(string="Work Order Currency Code")
    date_time_open = fields.Datetime(string="Date Time Opened")
    date_time_close = fields.Datetime(string="Date Time Closed")
    requestor_name = fields.Many2one('res.partner',string="Requestor Name",required=True)
    requestor_email = fields.Char(string="Requestor Email")
    requestor_phone = fields.Char(string="Requestor Phone")
    requestor_unit = fields.Many2one('product.template',string="Requestor Unit")

    def write(self, vals):
        if 'status' in vals and vals['status'] == 'closed':
            vals['date_time_close'] = fields.Datetime.now()
        return super(DlpCase, self).write(vals)

    # To create a sequence number.............
    @api.model
    def create(self, vals):
        if vals.get("seq_num", _('New')) == _('New'):
            vals['seq_num'] = self.env['ir.sequence'].next_by_code('dlp.case.seq') or _('New')
        res = super(DlpCase, self).create(vals)
        return res