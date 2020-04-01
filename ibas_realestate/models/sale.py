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
    unit_id = fields.Many2one('product.product', string='Unit', domain=[('is_a_property', '=', True),
                                                                        ('state', '=', 'open')])

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

        if self.unit_id.state != 'open':
            raise UserError(_('This property is already sold'))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'date_order': fields.Datetime.now()
        })
        self._action_confirm()

        if self.unit_id:
            self.unit_id.state = 'reserved'
            self.unit_id.customer = self.partner_id
            for prop in self.unit_id:
                prop.update({
                    'price_history_line_ids': [(0, 0, {
                        'effective_date': fields.Datetime.now(),
                        'selling_price': prop.list_price,
                        'pre_selling_price': prop.preselling_price,
                    })],
                })

            if len(self.sc_ids) > 0:
                myids = self.sc_ids.sorted(key=lambda r: r.date, reverse=True)
                self.unit_id.last_dp_date = myids[0].date

        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()
        return True

    @api.depends('unit_id', 'list_price')
    def _onchange_unit_id(self):
        for rec in self:
            if rec.unit_id.id is not False:
                rec.project_id = rec.unit_id.project_id.id
                rec.pre_selling_price = rec.unit_id.preselling_price
                rec.list_price = rec.unit_id.list_price
                rec.discount_amount = rec.pre_selling_price - rec.list_price
                rec.dp_terms = rec.unit_id.dp_terms

                self.update({
                    'order_line': [(5, 0, 0)]
                })

                self.update({
                    'order_line': [(0, 0, {
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

    sc_ids = fields.One2many(
        'ibas_realestate.sample_computation.line', 'order_id', string='Sample Computation')

    def action_compute_sc(self):
        for rec in self:
            if rec.unit_id.id is not False:
                self.update({
                    'sc_ids': [(5, 0, 0)]
                })

                self.update({
                    'sc_ids': [(0, 0, {
                        'date': datetime.today(),
                        'payment_amount': rec.reservation_amount,
                        'closing_fees': 0,
                        'description': 'Reservation',
                    })]
                })

                if rec.dp_terms:
                    i = 0
                    my_dp_term_int = int(rec.dp_terms)
                    monthly_closing_fees = rec.closing_fees / my_dp_term_int
                    monthly_fees = rec.downpayment / my_dp_term_int
                    if rec.is_cash:
                        monthly_fees = rec.downpayment - rec.discount_spotdp
                    while i < my_dp_term_int:
                        month_iteration = i + 1
                        mydate = datetime.today() + relativedelta(months=+month_iteration)

                        self.update({
                            'sc_ids': [(0, 0, {
                                'date': mydate,
                                'payment_amount': monthly_fees,
                                'closing_fees': monthly_closing_fees,
                                'description': 'Monthly',
                            })]
                        })
                        i = i + 1

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

    is_cash = fields.Boolean(string='Cash DP')

    @api.onchange('is_cash')
    def _onchange_is_cash(self):
        if self.unit_id:
            if self.is_cash:
                self.dp_terms = '1'
            else:
                self.dp_terms = self.unit_id.dp_terms

    monthly_10 = fields.Monetary(
        compute='_compute_monthly_10', string='Monthly Amortization 10 Years')

    interest_rate = fields.Float(
        string='Interest Rate', default=0.075, digits=(3, 3))

    @api.depends('loanable_amount', 'interest_rate')
    def _compute_monthly_10(self):
        for rec in self:
            rec.monthly_10 = calculate_amortization_amount(
                rec.loanable_amount, rec.interest_rate / 12, 120)

    monthly_20 = fields.Monetary(
        compute='_compute_monthly_20', string='Monthly Amortization 20 Years')

    @api.depends('loanable_amount', 'interest_rate')
    def _compute_monthly_20(self):
        for rec in self:
            rec.monthly_20 = calculate_amortization_amount(
                rec.loanable_amount, rec.interest_rate / 12, 240)

    loanable_amount = fields.Monetary(
        compute='_compute_loanable_amount', string='Loanable Amount')

    @api.depends('list_price', 'downpayment')
    def _compute_loanable_amount(self):
        for rec in self:
            rec.loanable_amount = rec.list_price - rec.downpayment - rec.reservation_amount


class SalesSampleComputationLine(models.Model):
    _name = 'ibas_realestate.sample_computation.line'
    _description = 'Sample Computation Line'

    currency_id = fields.Many2one('res.currency', related="company_id.currency_id",
                                  required=True, string='Currency', help="Main currency of the company.")
    company_id = fields.Many2one('res.company', string='Company',  required=True,
                                 default=lambda self: self.env.company.id)
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
