# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class IBASAccountPayment(models.Model):
    _inherit = 'account.payment'

    check_number = fields.Char(string='Check Number')
