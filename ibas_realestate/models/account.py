# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning, UserError, ValidationError


class IBASAccount(models.Model):
    _inherit = 'account.move'

    payment_ids = fields.Many2many('account.payment', 'account_invoice_payment_rel',
                                   'invoice_id', 'payment_id', string="Payments", copy=False)

    payment_count = fields.Integer(
        string="Payment Count", compute='_compute_payment')

    @api.depends("payment_ids")
    def _compute_payment(self):
        if self.payment_ids:
            self.payment_count = len(self.payment_ids)
        else:
            self.payment_count = 0

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state')
    def _compute_amount(self):

        invoice_ids = [move.id for move in self if move.id and move.is_invoice(
            include_receipts=True)]
        self.env['account.payment'].flush(['state'])
        if invoice_ids:
            self._cr.execute(
                '''
                    SELECT move.id
                    FROM account_move move
                    JOIN account_move_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN account_move_line rec_line ON
                        (rec_line.id = part.credit_move_id AND line.id = part.debit_move_id)
                        OR
                        (rec_line.id = part.debit_move_id AND line.id = part.credit_move_id)
                    JOIN account_payment payment ON payment.id = rec_line.payment_id
                    JOIN account_journal journal ON journal.id = rec_line.journal_id
                    WHERE payment.state IN ('posted', 'sent')
                    AND journal.post_at = 'bank_rec'
                    AND move.id IN %s
                ''', [tuple(invoice_ids)]
            )
            in_payment_set = set(res[0] for res in self._cr.fetchall())
        else:
            in_payment_set = {}

        for move in self:
            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            currencies = set()

            for line in move.line_ids:
                if line.currency_id:
                    currencies.add(line.currency_id)

                # Untaxed amount.
                if (move.is_invoice(include_receipts=True) and not line.exclude_from_invoice_tab) \
                        or (move.type == 'entry' and line.debit and not line.tax_line_id):
                    total_untaxed += line.balance
                    total_untaxed_currency += line.amount_currency

                # Tax amount.
                if line.tax_line_id:
                    total_tax += line.balance
                    total_tax_currency += line.amount_currency

                # Residual amount.
                if move.type == 'entry' or line.account_id.user_type_id.type in ('receivable', 'payable'):
                    total_residual += line.amount_residual
                    total_residual_currency += line.amount_residual_currency

            total = total_untaxed + total_tax
            total_currency = total_untaxed_currency + total_tax_currency

            if move.type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1

            if move.discount_rate != 0:
                move.amount_discount = move.discount_rate
            move.amount_untaxed = sign * \
                (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            move.amount_tax = sign * \
                (total_tax_currency if len(currencies) == 1 else total_tax)
            move.amount_total = sign * \
                (total_currency if len(currencies) == 1 else total)
            move.amount_residual = -sign * \
                (total_residual_currency if len(currencies) == 1 else total_residual)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = -total
            move.amount_residual_signed = total_residual

            currency = len(currencies) == 1 and currencies.pop(
            ) or move.company_id.currency_id
            is_paid = currency and currency.is_zero(
                move.amount_residual) or not move.amount_residual

            # Compute 'invoice_payment_state'.
            if move.state == 'posted' and is_paid:
                if move.id in in_payment_set:
                    move.invoice_payment_state = 'in_payment'
                else:
                    move.invoice_payment_state = 'paid'
            else:
                move.invoice_payment_state = 'not_paid'

    # discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount Type',
    #
    #                          readonly=True, states={'draft': [('readonly', False)]}, default='percent')

    unit_id = fields.Many2one('product.product', string='Unit', domain=[
                              ('is_a_property', '=', True), ('state', '=', 'open')])

    downpayment = fields.Monetary(string='Downpayment')
    discount_rate = fields.Float('Discount Amount', digits=(16, 2), readonly=True,
                                 states={'draft': [('readonly', False)]}, compute='_compute_discount_rate')

    disc_spot = fields.Monetary(string='Discount Spot DP')
    disc_amount = fields.Monetary(string='Discount Amount')

    amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_compute_amount',
                                      track_visibility='always')

    @api.depends('disc_spot', 'disc_amount')
    def _compute_discount_rate(self):
        for rec in self:
            if rec.disc_spot != 0 or rec.disc_amount != 0:
                rec.discount_rate += rec.disc_spot
                rec.discount_rate += rec.disc_amount
            else:
                rec.discount_rate += (rec.disc_amount + rec.disc_spot)

    @api.onchange('discount_rate', 'invoice_line_ids', 'disc_spot', 'disc_amount')
    def supply_rate(self):
        for inv in self:
            total = discount = 0.0
            for line in inv.invoice_line_ids:
                total += (line.quantity * line.price_unit)
            if inv.discount_rate != 0:
                discount = (inv.discount_rate / total) * 100
            else:
                discount = inv.discount_rate
            for line in inv.line_ids:
                line.discount = discount
                line._onchange_price_subtotal()

            inv._compute_invoice_taxes_by_group()

    def create_voucher(self):
        if self.line_ids:
            paymethod_obj = self.env['account.payment.method']
            payment_type = 'inbound'
            payment_method = paymethod_obj.search(
                [('payment_type', '=', payment_type)])
            if payment_method:
                payment_method_id = payment_method[0]
            else:
                raise UserError("No payment method defined.")

            for line in self.line_ids:
                if line.debit > 0:
                    journal_id = self.env['account.journal'].search(
                        [('company_id', '=', self.env.company.id), ('type', 'in', ('bank', 'cash'))], limit=1).id
                    payment_data = {
                        'journal_id': journal_id,
                        'payment_method_id': payment_method_id.id,
                        'payment_date': line.date_maturity,  # fields.Date.today(),
                        'communication': line.name,
                        'invoice_ids': [(4, self.id)],
                        # 'invoice_ids': [(4, inv.id, None) for inv in self._get_invoices(payment)],
                        'payment_type': payment_type,
                        'amount': line.debit,
                        'currency_id': self.currency_id.id,
                        # 'move_line_ids': [(4, line.id)],
                        'partner_id': line.partner_id.id,
                        'partner_type': 'customer',
                    }
                    if line.payment_id:
                        raise UserError("Payment Already Created")
                    else:
                        payrec = self.env['account.payment'].create(
                            payment_data)
                        # payrec.post()

                # self.env.user.notify_info(
                #    'Payment transactions are posted and customer account was updated.', title='Payment Posting', sticky=False)
        else:
            raise UserError(
                "No Journal Items")


class IBASAccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    discount = fields.Float(string='Discount (%)',
                            digits=(16, 20), default=0.0)
