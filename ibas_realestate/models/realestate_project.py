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

    preselling_price = fields.Float(string='Pre Selling Price')

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
    ], string='Status', default='open')

    customer = fields.Many2one('res.partner', string='Customer')
    propmodel_id = fields.Many2one('ibas_realestate.propertymodel', string='Model')

class IBASPropModel(models.Model):
    _name = 'ibas_realestate.propertymodel'
    _description = 'Property Model'

    name = fields.Char(string='Name', required=True)
    project_id = fields.Many2one('ibas_realestate.project', string='Project')


