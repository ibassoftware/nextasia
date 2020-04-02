# -*- coding : utf-8 -*-

import time

import odoo.addons.decimal_precision as dp

from odoo import models, fields, api, tools, _
from odoo.exceptions import Warning, UserError, ValidationError


class IBASUpdateSalePrice(models.TransientModel):
    _name = "ibas_realestate.update_sale_price_wiz"
    _description = "Update Sale Price Wizard"

    @api.model
    def _default_product_id(self):
        if self._context.get('active_ids'):
            prod_obj = self.env['product.product']
            prod = prod_obj.browse(self._context.get('active_ids'))[0]
            return prod.id
        else:
            return 0

    product_id = fields.Many2one(
        'product.product', string='Property', default=_default_product_id)
    selling_price = fields.Float(string='Sale Price')
    pre_selling_price = fields.Float(string='Pre Selling Price')

    def update_price(self):
        if self.product_id:
            for prop in self.product_id:
                prop.update({
                    'price_history_line_ids': [(0, 0, {
                        'effective_date': fields.Datetime.now(),
                        'selling_price': self.selling_price,
                        'pre_selling_price': self.pre_selling_price,
                    })],
                    'list_price': self.selling_price,
                    'preselling_price': self.pre_selling_price,
                })

         # Open Properties Form
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object(
            'ibas_realestate.ire_ibas_property_action')
        form_view_id = imd.xmlid_to_res_id(
            'ibas_realestate.ire_property_view_form')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[form_view_id, 'form']],
            'target': action.target,
            # 'context': action.context,
            'res_model': action.res_model,
            'res_id': self.product_id.id,
        }
        result['domain'] = "[('id','=',%s)]" % self.product_id.id
        return result
