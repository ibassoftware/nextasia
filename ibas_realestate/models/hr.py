# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class IBASHr(models.Model):
    _inherit = 'hr.employee'

    contact_broker_ids = fields.One2many(
        'res.partner', 'broker', string='Contact Broker')
    contact_agent_ids = fields.One2many(
        'res.partner', 'agent', string='Contact Agent')
    contact_sales_manager_ids = fields.One2many(
        'res.partner', 'sales_manager', string='Sales Manager')
    contact_nali_coordinator_ids = fields.One2many(
        'res.partner', 'nali_coordinator', string='Nali Coordinator')
