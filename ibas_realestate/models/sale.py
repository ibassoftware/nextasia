# -*- coding: utf-8 -*-

import logging
from amortization.amount import calculate_amortization_amount
from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime
from dateutil.relativedelta import *
import math


_logger = logging.getLogger(__name__)


class IBASSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    disc = fields.Float(string='Discount')


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
            self.unit_id.reservation_date = False
            self.unit_id.so_selling_price = 0.00

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
            self.unit_id.reservation_date = self.date_order
            self.unit_id.so_selling_price = self.list_price
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
                # rec.discount_amount = rec.pre_selling_price - rec.list_price
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
    list_price = fields.Float(string='Selling Price')

    discount_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage'),
    ], string='Discount Type')

    discount_amount = fields.Float(string='Discount Amount', store=True)
    discount_amount_percent = fields.Float(
        string='Discount Amount', compute="_compute_discount_price")

    discount_rate_id = fields.Many2one(
        'sale.discount.rate', string="Discount Rate")

    discounted_price = fields.Float(
        string="Discounted Price", compute="_compute_discount_price")

    downpayment = fields.Monetary(string='Downpayment')
    reservation_amount = fields.Monetary(string='Reservation')
    closing_fees = fields.Monetary(string='Closing Fees')
    discount_spotdp = fields.Monetary(string='Spot DP Discount')
    disc_spot = fields.Monetary(
        string='Discount Spot DP', compute='_disc_spot')
    disc_amount = fields.Monetary(
        string='Discount Amount', compute='_disc_amount')

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal = self.env['account.move'].with_context(
            force_company=self.company_id.id, default_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (
                self.company_id.name, self.company_id.id))

        invoice_vals = {
            'ref': self.client_order_ref or '',
            'type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.pricelist_id.currency_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_payment_ref': self.reference,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
            'disc_spot': self.disc_spot,
            'disc_amount': self.disc_amount,
        }
        return invoice_vals

    @api.depends('discount_spotdp')
    def _disc_spot(self):
        for rec in self:
            rec.update({
                'disc_spot': rec.discount_spotdp,
            })

    @api.depends('discount_amount_percent', 'discount_amount')
    def _disc_amount(self):
        for rec in self:
            if self.discount_type == 'fixed':
                rec.update({
                    'disc_amount': rec.discount_amount,
                })

            elif self.discount_type == 'percentage':
                rec.update({
                    'disc_amount': rec.discount_amount_percent,
                })

            else:
                rec.update({
                    'disc_amount': 0.0,
                })

    @api.depends('order_line.price_total', 'discount_amount_percent', 'discount_spotdp')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax - (self.disc_amount + self.discount_spotdp),
            })

    @api.onchange('discount_type')
    def _onchange_discount_type(self):
        for rec in self:
            if rec.discount_type == "fixed":
                rec.discount_amount_percent = 0.0

            elif rec.discount_type == "percentage":
                rec.discount_amount = 0.0

            else:
                rec.discount_amount_percent = 0.0
                rec.discount_amount = 0.0

    @api.depends('discount_amount', 'discount_rate_id', 'discount_type')
    def _compute_discount_price(self):
        for rec in self:
            if rec.discount_type == "fixed":
                rec.discounted_price = rec.list_price - rec.discount_amount
                rec.discount_amount_percent = 0.0

            elif rec.discount_type == "percentage":
                rec.discount_amount_percent = rec.list_price * rec.discount_rate_id.rate
                rec.discounted_price = rec.list_price - rec.discount_amount_percent

            else:
                rec.discounted_price = rec.list_price
                rec.discount_amount_percent = 0.0

    @api.onchange('list_price')
    def _onchange_list_price(self):
        for rec in self:
            rec.downpayment = rec.list_price * 0.10 - 5000  # 50000
            rec.reservation_amount = 5000  # 50000
            rec.closing_fees = rec.list_price * 0.05

    sc_ids = fields.One2many(
        'ibas_realestate.sample_computation.line', 'order_id', string='Sample Computation')

    def ord(self, n):
        return str(n)+("th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))

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
                        monthly_fees = rec.downpayment  # - rec.discount_spotdp
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

    ], string='DP Terms',
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    is_cash = fields.Boolean(string='Cash DP')

    downpayment_type = fields.Selection(
        [('fixed', 'Fixed'), ('percentage', 'Percentage')], string='Downpayment Type')
    dp_per_rate = fields.Many2one(
        'sale.downpayment.rate', string='DP Rate Percentage')
    downpayment_per_rate = fields.Selection(
        [('6_5', '6.5%'), ('8_5', '8.5%'), ('10', '10%')], string='DP Percentage Rate')

    financing_type = fields.Selection(
        [('phdmf', 'Pag-IBIG'), ('bankf', 'Bank Financing')], string='Financing Type', default='phdmf')

    @api.onchange('financing_type')
    def _Onchangefinancetype(self):

        if self.financing_type == 'phdmf':
            self.interest_rate = 0.06375
        else:
            self.interest_rate = 0.07500

    @api.onchange('downpayment_type', 'dp_per_rate', 'discount_spotdp', 'is_cash', 'reservation_amount', 'discount_type', 'discount_amount', 'discount_rate_id')
    def changeDownpaymentAmount(self):
        if self.downpayment_type == 'fixed':
            self.downpayment = self.list_price * 0.10 - 5000
            rate = self.dp_per_rate = False
        else:
            if not self.dp_per_rate:
                self.dp_per_rate = self.env.ref('ibas_realestate.rate_10_0').id

            rate = self.dp_per_rate and self.dp_per_rate.rate / 100.00

            amount = 0
            if self.discount_type:
                amount += self.discounted_price * rate

            if self.discount_spotdp >= 0:
                dp_amount = amount - \
                    (self.reservation_amount + self.discount_spotdp)
                self.downpayment = dp_amount

            if not self.is_cash:
                self.discount_spotdp = 0.0

            if self.reservation_amount >= 0:
                dp_amount = amount - \
                    (self.reservation_amount + self.discount_spotdp)
                self.downpayment = dp_amount

    @api.onchange('dp_terms')
    def _onchange_dp_terms(self):
        if self.unit_id:
            self.unit_id.dp_terms = self.dp_terms

    @api.onchange('is_cash')
    def _onchange_is_cash(self):
        if self.unit_id:
            if self.is_cash:
                self.dp_terms = '1'
                self.unit_id.dp_terms = '1'
            else:
                self.dp_terms = self.unit_id.dp_terms

    monthly_3 = fields.Monetary(
        compute='_compute_monthly_3', string='Monthly Amortization 3 Years')

    monthly_5 = fields.Monetary(
        compute='_compute_monthly_5', string='Monthly Amortization 5 Years')

    monthly_10 = fields.Monetary(
        compute='_compute_monthly_10', string='Monthly Amortization 10 Years')

    monthly_20 = fields.Monetary(
        compute='_compute_monthly_20', string='Monthly Amortization 20 Years')

    monthly_30 = fields.Monetary(
        compute='_compute_monthly_30', string='Monthly Amortization 30 Years')

    interest_rate = fields.Many2one(
        'sale.interest.rate', string='Interest Rate')

    @api.model
    def default_get(self, fields):
        res = super(IBASSale, self).default_get(fields)
        res['interest_rate'] = 2
        return res

    @api.depends('loanable_amount', 'interest_rate')
    def _compute_monthly_3(self):
        if self.interest_rate:
            for rec in self:
                rec.monthly_3 = calculate_amortization_amount(
                    rec.loanable_amount, rec.interest_rate.rate / 12, 36)
        else:
            for rec in self:
                rec.monthly_3 = calculate_amortization_amount(
                    rec.loanable_amount, 0.06375 / 12, 36)

    @api.depends('loanable_amount', 'interest_rate')
    def _compute_monthly_5(self):
        if self.interest_rate:
            for rec in self:
                rec.monthly_5 = calculate_amortization_amount(
                    rec.loanable_amount, rec.interest_rate.rate / 12, 60)
        else:
            for rec in self:
                rec.monthly_5 = calculate_amortization_amount(
                    rec.loanable_amount, 0.06375 / 12, 60)

    @api.depends('loanable_amount', 'interest_rate')
    def _compute_monthly_10(self):
        if self.interest_rate:
            for rec in self:
                rec.monthly_10 = calculate_amortization_amount(
                    rec.loanable_amount, rec.interest_rate.rate / 12, 120)
        else:
            for rec in self:
                rec.monthly_10 = calculate_amortization_amount(
                    rec.loanable_amount, 0.06375 / 12, 120)

    @api.depends('loanable_amount', 'interest_rate')
    def _compute_monthly_20(self):
        if self.interest_rate:
            for rec in self:
                rec.monthly_20 = calculate_amortization_amount(
                    rec.loanable_amount, rec.interest_rate.rate / 12, 240)
        else:
            for rec in self:
                rec.monthly_20 = calculate_amortization_amount(
                    rec.loanable_amount, 0.06375 / 12, 240)

    @api.depends('loanable_amount', 'interest_rate')
    def _compute_monthly_30(self):
        if self.interest_rate:
            for rec in self:
                rec.monthly_30 = calculate_amortization_amount(
                    rec.loanable_amount, rec.interest_rate.rate / 12, 360)
        else:
            for rec in self:
                rec.monthly_30 = calculate_amortization_amount(
                    rec.loanable_amount, 0.06375 / 12, 360)

    loanable_amount = fields.Monetary(
        compute='_compute_loanable_amount', string='Loanable Amount')

    @api.depends('list_price', 'downpayment')
    def _compute_loanable_amount(self):
        for rec in self:
            rec.loanable_amount = rec.list_price - rec.downpayment - rec.reservation_amount
    # For Reports
    current_date = fields.Datetime('Date', compute='_compute_report_gen_date')

    def _compute_report_gen_date(self):
        for rec in self:
            rec.current_date = fields.Datetime.now()


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


class SaleDownPaymentRate(models.Model):
    _name = 'sale.downpayment.rate'
    _description = 'Downpayment Rate'

    name = fields.Char('Name', required=True)
    rate = fields.Float(string='Rate %', digits=(5, 5))


class SaleInterestRate(models.Model):
    _name = 'sale.interest.rate'
    _description = 'Interest Rate'

    name = fields.Char('Name', required=True)
    rate = fields.Float(string='Rate', digits=(5, 5))


class SaleDiscountRate(models.Model):
    _name = 'sale.discount.rate'
    _description = 'Discount Rate'

    name = fields.Char('Name', required=True)
    rate = fields.Float(string='Rate', digits=(5, 5))
