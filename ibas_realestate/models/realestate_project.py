# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models
from odoo.exceptions import Warning, UserError, ValidationError

_logger = logging.getLogger(__name__)


class custom_partner(models.Model):
    _inherit = "res.partner"

    is_company = fields.Boolean(default=False)


class IBASREProject(models.Model):
    _name = 'ibas_realestate.project'
    _description = 'Real Estate Project'

    name = fields.Char(string='Project Name', required=True)


class PropertiesProjectProperty(models.Model):
    _inherit = 'product.product'
    _description = 'Real Estate Properties'
    _sql_constraints = [('name_uniq', 'unique (name)',
                         'Duplicate products not allowed !')]

    is_a_property = fields.Boolean(string='Is A Property')

    currency_id = fields.Many2one('res.currency', related="company_id.currency_id",
                                  required=True, string='Currency', help="Main currency of the company.")
    company_id = fields.Many2one('res.company', string='Company',  required=True,
                                 default=lambda self: self.env.company.id)

    @api.onchange('project_id', 'block', 'lot', 'phase')
    def _compute_name(self):
        for rec in self:
            if rec.is_a_property:
                for rec in self:
                    try:
                        rec.name = rec.project_id.name + ' Block ' + \
                            rec.block + ' Lot ' + rec.lot + ' Phase' + rec.phase
                    except:
                        pass

    project_id = fields.Many2one('ibas_realestate.project', string='Project')
    block = fields.Char(string='Block')
    lot = fields.Char(string='Lot')
    phase = fields.Char('Phase')

    preselling_price = fields.Monetary(string='Pre Selling Price')

    responsible = fields.Many2one('res.users', string='Account Officer')
    contractor = fields.Many2one('res.partner', string='Contractor')
    construction_start_date = fields.Date(string='Construction Start Date')
    construction_end_date = fields.Date(string='Construction End Date')
    actual_construction_complete_date = fields.Date(
        string='Actual Construction Completion Date')
    financing_type = fields.Selection([
        ('na', 'NA'),
        ('bank', 'Bank'),
        ('pagibig', 'Pag-Ibig'),
        ('cash', 'Cash')
    ], string='Financing')

    state = fields.Selection([
        ('open', 'Available'),
        ('reserved', 'Reservation Sale'),
        ('booked', 'Booked Sale'),
        ('contracted', 'Contracted Sale'),
        ('proceed', 'Loan Proceeds'),
        ('accept', 'Acceptance'),
    ], string='Status', default='open', tracking=True)

    customer = fields.Many2one('res.partner', string='Customer')
    propmodel_id = fields.Many2one(
        'ibas_realestate.propertymodel', string='Model')

    last_dp_date = fields.Date(string='Last DP Date')
    dp_terms = fields.Selection([
        ('1', '1 Month'),
        ('2', '2 Months'),
        ('3', '3 Months'),
        ('4', '4 Months'),
        ('5', '5 Months'),
        ('6', '6 Months'),
        ('7', '7 Months'),
        ('8', '8 Months'),
        ('9', '9 Months'),
        ('10', '10 Months'),
        ('11', '11 Months'),
        ('12', '12 Months'),
        ('13', '13 Months'),
        ('14', '14 Months'),
        ('15', '15 Months'),
        ('16', '16 Months'),
        ('17', '17 Months'),
        ('18', '18 Months'),
        ('19', '19 Months'),
        ('20', '20 Months'),
        ('21', '21 Months'),
        ('22', '22 Months'),
        ('23', '23 Months'),
        ('24', '24 Months'),

    ], string='DP Terms')

    propclass_id = fields.Many2one(
        'ibas_realestate.property_class', string='Type')
    floor_area = fields.Float(string='Floor Area (sqm)')
    lot_area = fields.Float(string='Lot Area (sqm)')

    reservation_line_ids = fields.One2many(
        'ibas_realestate.requirement_reservation_line', 'product_id', string='Reservation')
    booked_sale_line_ids = fields.One2many(
        'ibas_realestate.requirement_booked_sale_line', 'product_id', string='Booked Sale')
    contracted_sale_line_ids = fields.One2many(
        'ibas_realestate.requirement_contracted_sale_line', 'product_id', string='Contracted Sale')

    loan_proceeds_line_ids = fields.One2many(
        'ibas_realestate.requirement_loan_proceeds_line', 'product_id', string='Loan Proceeds')

    price_history_line_ids = fields.One2many(
        'ibas_realestate.price_history_line', 'product_id', string='Price History')

    on_hold = fields.Boolean('Tech Hold')

    @api.constrains('name')
    def _check_names(self):
        name = self.env['product.product'].search(
            [('name', '=', self.name)])
        if name:
            for n in name:
                if n.id != self.id:
                    raise ValidationError("Duplicate Record")

    def unlink(self):
        for rec in self:
            if rec.name:
                raise UserError(_('You cannot delete record.'))
            return super(PropertiesProjectProperty, self).unlink()

    def tech_hold(self):
        self.on_hold = True

    def release_hold(self):
        self.on_hold = False

    def acceptance(self):
        if self.loan_proceeds_line_ids:
            for line in self.loan_proceeds_line_ids:
                if line.complied == True:
                    self.state = 'accept'
                else:
                    raise ValidationError(
                        'Not all Loan Proceeds Requirements are submitted. Please upload submitted files before confirming.')
        else:
            raise ValidationError(
                'There are no Loan proceeds requirements in the list')

        sale_obj = self.env['sale.order']
        sale_order = sale_obj.search(
            [('unit_id', '=', self.id), ('state', '=', 'sale')])

        if sale_order:
            for sale in sale_order:
                sale.state = 'done'

    def loan_proceeds(self):
        client_reqs = self.env['ibas_realestate.client_requirement'].search(
            [('default_requirement', '=', True), ('stage', '=', 'proceeds')])
        client_lines = []
        if self.state == 'contracted':
            for req in client_reqs:
                client_line = {
                    'requirement': req.id
                }
                client_lines.append(client_line)
        if self.contracted_sale_line_ids:
            for line in self.contracted_sale_line_ids:
                if line.complied == True:
                    self.state = 'proceed'
                else:
                    raise ValidationError(
                        'Not all Contracted Requirements are submitted. Please upload submitted files before confirming.')
        else:
            raise ValidationError(
                'There are no Contracted Sale requirements in the list')

        if len(client_lines) > 0:
            loan_proceeds_lines = []
            for client in client_lines:
                if not self.loan_proceeds_line_ids:
                    loan_proceeds_lines.append((0, 0, client))
            self.update({'loan_proceeds_line_ids': loan_proceeds_lines})
        else:
            raise UserError('There are no client requirements')

    def get_requirements(self):
        for rec in self:
            if rec.state == 'reserved':
                self.update({
                    'reservation_line_ids': [(5, 0, 0)]
                })

                def_reqts = self.env['ibas_realestate.client_requirement'].search(
                    [('default_requirement', '=', True), ('stage', '=', 'reservation')])
                if def_reqts:
                    for target_list in def_reqts:
                        self.update({
                            'reservation_line_ids': [(0, 0, {
                                'requirement': target_list.id,
                            })],
                        })
                else:
                    raise ValidationError(
                        'There are no Reservation Requirements Created.')

    def booked_sale(self):
        client_reqs = self.env['ibas_realestate.client_requirement'].search(
            [('default_requirement', '=', True), ('stage', '=', 'booked')])
        client_lines = []
        if self.state == 'reserved':
            for req in client_reqs:
                client_line = {
                    'requirement': req.id
                }
                client_lines.append(client_line)
        if self.reservation_line_ids:
            for line in self.reservation_line_ids:
                if line.complied == True:
                    self.state = 'booked'
                else:
                    raise ValidationError(
                        'Not all Reservation Sale Requirements are submitted. Please upload submitted files before confirming.')
        else:
            raise ValidationError(
                'There are no Reservation Sale requirements in the list')

        if len(client_lines) > 0:
            booked_lines = []
            for client in client_lines:
                if not self.booked_sale_line_ids:
                    booked_lines.append((0, 0, client))
            self.update({'booked_sale_line_ids': booked_lines})
        else:
            raise UserError('There are no client requirements')

    def contracted_sale(self):
        client_reqs = self.env['ibas_realestate.client_requirement'].search(
            [('default_requirement', '=', True), ('stage', '=', 'contracted')])
        client_lines = []
        if self.state == 'booked':
            for req in client_reqs:
                client_line = {
                    'requirement': req.id
                }
                client_lines.append(client_line)
        if self.booked_sale_line_ids:
            for line in self.booked_sale_line_ids:
                if line.complied == True:
                    self.state = 'contracted'
                else:
                    raise ValidationError(
                        'Not all Booked Sale Requirements are submitted. Please upload submitted files before confirming.')
        else:
            raise ValidationError(
                'There are no Booked Sale requirements in the list')

        if len(client_lines) > 0:
            contracted_lines = []
            for client in client_lines:
                if not self.contracted_sale_line_ids:
                    contracted_lines.append((0, 0, client))
            self.update({'contracted_sale_line_ids': contracted_lines})
        else:
            raise UserError('There are no client requirements')

    # back to

    def back_to_reservation(self):
        for rec in self:
            rec.state = 'reserved'

    def back_to_booked(self):
        for rec in self:
            rec.state = 'booked'

    def back_to_contracted(self):
        for rec in self:
            rec.state = 'contracted'

     ####

    def open_view_form(self):
        return {
            'name': 'Property Form',  # Lable
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('ibas_realestate.ire_property_view_form').id,
            'res_model': 'product.product',  # your model
            'res_id': self.id
        }


class IBASPropModel(models.Model):
    _name = 'ibas_realestate.propertymodel'
    _description = 'Property Model'

    name = fields.Char(string='Name', required=True)
    project_id = fields.Many2one('ibas_realestate.project', string='Project')


class IBASRequirementModel(models.Model):
    _name = 'ibas_realestate.client_requirement'
    _description = 'Client Requirements'

    name = fields.Char(string='Name', required=True)
    default_requirement = fields.Boolean(string='Default')
    stage = fields.Selection([('reservation', 'Reservation'),
                              ('booked', 'Booked Sale'), ('contracted', 'Contracted Sale'), ('proceeds', 'Loan Proceeds')], string="Stage")

# reservation


class IBASPropertyRequirementReservationLine(models.Model):
    _name = 'ibas_realestate.requirement_reservation_line'
    _description = 'Requirement Reservation Line'

    parent_id = fields.Many2one('res.partner', string="customer")
    product_id = fields.Many2one('product.product', string='Property')
    requirement = fields.Many2one(
        'ibas_realestate.client_requirement', string='Reservation', domain=[('stage', '=', 'reservation')])
    compliance_date = fields.Date(string='Date Complied')
    requirement_file = fields.Binary(string='File Attachment')
    complied = fields.Boolean(compute='_compute_complied', string='Complied')

    @api.depends('requirement_file')
    def _compute_complied(self):
        for rec in self:
            if rec.requirement_file:
                rec.complied = True
            else:
                rec.complied = False

# booked sale


class IBASPropertyRequirementBookedSaleLine(models.Model):
    _name = 'ibas_realestate.requirement_booked_sale_line'
    _description = 'Requirement Booked Sale Line'

    parent_id = fields.Many2one('res.partner', string="customer")
    product_id = fields.Many2one('product.product', string='Property')
    requirement = fields.Many2one(
        'ibas_realestate.client_requirement', string='Booked Sale', domain=[('stage', '=', 'booked')])
    compliance_date = fields.Date(string='Date Complied')
    requirement_file = fields.Binary(string='File Attachment')
    complied = fields.Boolean(compute='_compute_complied', string='Complied')

    @api.depends('requirement_file')
    def _compute_complied(self):
        for rec in self:
            if rec.requirement_file:
                rec.complied = True
            else:
                rec.complied = False

# contracted sale


class IBASPropertyRequirementContractedSaleLine(models.Model):
    _name = 'ibas_realestate.requirement_contracted_sale_line'
    _description = 'Requirement Contracted Sale Line'

    parent_id = fields.Many2one('res.partner', string="customer")
    product_id = fields.Many2one('product.product', string='Property')
    requirement = fields.Many2one(
        'ibas_realestate.client_requirement', string='Contracted Sale', domain=[('stage', '=', 'contracted')])
    compliance_date = fields.Date(string='Date Complied')
    requirement_file = fields.Binary(string='File Attachment')
    complied = fields.Boolean(compute='_compute_complied', string='Complied')

    @api.depends('requirement_file')
    def _compute_complied(self):
        for rec in self:
            if rec.requirement_file:
                rec.complied = True
            else:
                rec.complied = False


class IBASPropertyRequirementLoanProceedsLine(models.Model):
    _name = 'ibas_realestate.requirement_loan_proceeds_line'
    _description = 'Requirement Loan Proceeds Line'

    parent_id = fields.Many2one('res.partner', string="customer")
    product_id = fields.Many2one('product.product', string='Property')
    requirement = fields.Many2one(
        'ibas_realestate.client_requirement', string='Loan Proceeds', domain=[('stage', '=', 'proceed')])
    compliance_date = fields.Date(string='Date Complied')
    requirement_file = fields.Binary(string='File Attachment')
    complied = fields.Boolean(compute='_compute_complied', string='Complied')

    @api.depends('requirement_file')
    def _compute_complied(self):
        for rec in self:
            if rec.requirement_file:
                rec.complied = True
            else:
                rec.complied = False

# Price History


class IBASPropertyPriceHistoryLine(models.Model):
    _name = 'ibas_realestate.price_history_line'
    _description = 'Price History'
    _order = "effective_date desc"

    product_id = fields.Many2one('product.product', string='Property')
    effective_date = fields.Datetime(string='Effective Date')
    selling_price = fields.Float(string='Sale Price')
    pre_selling_price = fields.Float(string='Pre Selling Price')
    user_id = fields.Many2one('res.users', string='Update By:',
                              required=True, default=lambda self: self.env.uid)


class PropertyClass(models.Model):
    _name = 'ibas_realestate.property_class'
    _description = 'Property Class'

    name = fields.Char(string='Class', required=True)
    _sql_constraints = [
        ('unique_properties_name', 'UNIQUE(name)',
         'You can not have two properties')
    ]
