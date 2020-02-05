# -*- coding: utf-8 -*-
# from odoo import http


# class IbasRealestate(http.Controller):
#     @http.route('/ibas_realestate/ibas_realestate/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ibas_realestate/ibas_realestate/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ibas_realestate.listing', {
#             'root': '/ibas_realestate/ibas_realestate',
#             'objects': http.request.env['ibas_realestate.ibas_realestate'].search([]),
#         })

#     @http.route('/ibas_realestate/ibas_realestate/objects/<model("ibas_realestate.ibas_realestate"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ibas_realestate.object', {
#             'object': obj
#         })
