# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

class IBASREProject(models.Model):
    _name = 'ibas_realestate.project'
    _description = 'Real Estate Project'
    
    name = fields.Char(string='Project Name', required=True)



class PropertiesProjectProperty(models.Model):
    _inherit = 'product.product'
    _description = 'Real Estate Properties'

    is_a_property = fields.Boolean(string='Is A Property')

    currency_id = fields.Many2one('res.currency', related="company_id.currency_id", required=True, string='Currency', help="Main currency of the company.")
    company_id = fields.Many2one('res.company', string='Company',  required=True,
    default=lambda self: self.env.company.id)


    @api.onchange('project_id','block','lot')
    def _compute_name(self):
        for rec in self:
            if rec.is_a_property:            
                for rec in self:
                    try:
                        rec.name = rec.project_id.name + ' ' + rec.block + ' ' + rec.lot
                    except:
                        pass
                

    project_id = fields.Many2one('ibas_realestate.project', string='Project')
    block = fields.Char(string='Block')
    lot = fields.Char(string='Lot')

    preselling_price = fields.Monetary(string='Pre Selling Price')

    responsible = fields.Many2one('res.users', string='Responsible')
    contractor = fields.Many2one('res.partner', string='Contractor')
    construction_start_date = fields.Date(string='Construction Start Date')
    construction_end_date = fields.Date(string='Construction End Date')
    actual_construction_complete_date = fields.Date(string='Actual Construction Completion Date')
    financing_type = fields.Selection([
        ('na', 'NA'),
        ('bank', 'Bank'),
        ('pagibig', 'Pag-Ibig'),
        ('cash', 'Cash')
    ], string='Financing')

    state = fields.Selection([
        ('open', 'Open'),
        ('booked', 'Booked Sale'),
        ('contracted', 'Contracted Sale')
    ], string='Status', default='open', tracking=True)

    customer = fields.Many2one('res.partner', string='Customer')
    propmodel_id = fields.Many2one('ibas_realestate.propertymodel', string='Model')

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

    propclass_id = fields.Many2one('ibas_realestate.property_class', string='Class')    
    floor_area = fields.Float(string='Floor Area (sqm)')
    lot_area = fields.Float(string='Lot Area (sqm)')

    def mark_contracted(self):
        self.state = 'contracted'
    
    
    def get_requirements(self):
        for rec in self:
            if rec.state == 'booked':
                self.update({
                    'line_ids':[(5,0,0)]
                })

                def_reqts = self.env['ibas_realestate.client_requirement'].search([('default_requirement', '=', True)])
                for target_list in def_reqts:
                    self.update({
                    'line_ids': [(0,0,{
                        'requirement': target_list.id,
                    })]
                })
    
    line_ids = fields.One2many('ibas_realestate.requirement_line', 'product_id', string='Requirements')

    
    def open_view_form(self):
        return {
            'name': 'Property Form', # Lable
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('ibas_realestate.ire_property_view_form').id,
            'res_model': 'product.product', # your model
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
    
    name = fields.Char(string='Name', required= True)
    default_requirement = fields.Boolean(string='Default')

class IBASPropertyRequirementLine(models.Model):
    _name = 'ibas_realestate.requirement_line'
    _description = 'Requirement Line'
    
    product_id = fields.Many2one('product.product', string='Property')
    requirement = fields.Many2one('ibas_realestate.client_requirement', string='Requirement')
    compliance_date = fields.Date(string='Date Complied')
    requirement_file = fields.Binary(string='File Attachment')
    complied = fields.Boolean(string='Complied')

class ProeprtyClass(models.Model):
    _name = 'ibas_realestate.property_class'
    _description = 'Property Class'
    
    name = fields.Char(string='Class', required=True)


