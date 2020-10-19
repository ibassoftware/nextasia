# -*- coding: utf-8 -*-
import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class IBASSaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _create_invoice(self, order, so_line, amount):
        invoice_vals = super(IBASSaleAdvancePaymentInv,
                             self)._create_invoice(order, so_line, amount)

        invoice_vals.update({
            'unit_id': order.unit_id.id,
            'invoice_date': order.date_order
        })
        return invoice_vals
