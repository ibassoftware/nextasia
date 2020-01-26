# -*- coding: utf-8 -*-

import logging
from amortization.amount import calculate_amortization_amount
from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime
from dateutil.relativedelta import *


_logger = logging.getLogger(__name__)

class IBASSale(models.Model):
    _inherit = 'sale.order'
    unit_id = fields.Many2one('product.product', string='Unit', domain=[('is_a_property','=',True),
    ('state','=','open')])

    project_id = fields.Many2one('ibas_realestate.project', string='Project',
    compute="_onchange_unit_id", store=True)

    def action_cancel(self):

        if self.unit_id:
            self.unit_id.state = 'open'
            self.unit_id.customer = False
        return self.write({'state': 'cancel'})

    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'date_order': fields.Datetime.now()
        })
        self._action_confirm()

        if self.unit_id:
            self.unit_id.state = 'booked'
            self.unit_id.customer = self.partner_id

        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()
        return True

    @api.depends('unit_id','list_price')
    def _onchange_unit_id(self):
        for rec in self:
            if rec.unit_id.id is not False:
                rec.project_id = rec.unit_id.project_id.id
                rec.pre_selling_price = rec.unit_id.preselling_price
                rec.list_price = rec.unit_id.list_price
                rec.discount_amount = rec.pre_selling_price - rec.list_price

                self.update({
                    'order_line':[(5,0,0)]
                })
                
                self.update({
                    'order_line': [(0,0,{
                        'product_id': rec.unit_id.id,
                        'product_uom_qty': 1,
                        'price_unit': rec.list_price,
                        'name': rec.unit_id.name,
                        'customer_lead': 0
                    })]
                })

                for line in rec.order_line:
                    line.product_id_change() 
                


    
    pre_selling_price = fields.Float(string='Pre Selling Price')
    discount_amount = fields.Float(string='Discount')
    list_price = fields.Float(string='Discounted Price')

    downpayment = fields.Monetary(string='Downpayment')
    reservation_amount = fields.Monetary(string='Reservation')
    closing_fees = fields.Monetary(string='Closing Fees')
    discount_spotdp = fields.Monetary(string='Spot DP Discount')

    @api.onchange('list_price')
    def _onchange_list_price(self):
        for rec in self:
            rec.downpayment = rec.list_price * 0.20 - 50000
            rec.reservation_amount = 50000
            rec.closing_fees = rec.list_price * 0.05
    
    sc_ids = fields.One2many('ibas_realestate.sample_computation.line', 'order_id', string='Sample Computation')

    
    def action_compute_sc(self):
        for rec in self:
            if rec.unit_id.id is not False:
                self.update({
                    'sc_ids':[(5,0,0)]
                })

                self.update({
                    'sc_ids': [(0,0,{
                        'date': datetime.today(),
                        'payment_amount': rec.reservation_amount,
                        'closing_fees': 0,
                        'description': 'Reservation',
                    })]
                })

                if rec.dp_terms == 'monthly_12':
                    i = 0
                    monthly_closing_fees = rec.closing_fees / 12
                    monthly_fees = rec.downpayment / 12
                    while i < 12:
                        month_iteration  = i + 1
                        mydate = datetime.today() + relativedelta(months=+month_iteration)
                        self.update({
                            'sc_ids': [(0,0,{
                                'date': mydate,
                                'payment_amount': monthly_fees,
                                'closing_fees': monthly_closing_fees,
                                'description': 'Monthly',
                            })]
                        })      
                        i = i + 1

    dp_terms = fields.Selection([
        ('monthly_12', '12 Months')
    ], string='DP Terms', required=True)

    monthly_10 = fields.Monetary(compute='_compute_monthly_10', string='Monthly Amortization 10 Years')

    interest_rate = fields.Float(string='Interest Rate', default=0.075, digits=(3, 3))
    
    @api.depends('loanable_amount', 'interest_rate')
    def _compute_monthly_10(self):
        for rec in self:
            rec.monthly_10 = calculate_amortization_amount(rec.loanable_amount, rec.interest_rate / 12, 120)
    
    monthly_20 = fields.Monetary(compute='_compute_monthly_20', string='Monthly Amortization 20 Years')
    
    @api.depends('loanable_amount', 'interest_rate')
    def _compute_monthly_20(self):
        for rec in self:
            rec.monthly_20 = calculate_amortization_amount(rec.loanable_amount, rec.interest_rate / 12, 240)
    
    loanable_amount = fields.Monetary(compute='_compute_loanable_amount', string='Loanable Amount')
    
    @api.depends('list_price', 'downpayment')
    def _compute_loanable_amount(self):
        for rec in self:
            rec.loanable_amount =  rec.list_price - rec.downpayment - rec.reservation_amount


    
class SalesSampleComputationLine(models.Model):
    _name = 'ibas_realestate.sample_computation.line'
    _description = 'Sample Computation Line'

    currency_id = fields.Many2one('res.currency', related="company_id.currency_id", required=True, string='Currency', help="Main currency of the company.")
    company_id = fields.Many2one('res.company', string='Company',  required=True,
    default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
    date = fields.Date(string='Date')
    payment_amount = fields.Monetary(string='Amount')
    closing_fees = fields.Monetary(string='Closing Fees')
    description = fields.Char(string='Description')
    total = fields.Monetary(compute='_compute_total', string='Total')

    order_id = fields.Many2one('sale.order', string='Order ID')
    
    @api.depends('payment_amount', 'closing_fees')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.payment_amount + rec.closing_fees






