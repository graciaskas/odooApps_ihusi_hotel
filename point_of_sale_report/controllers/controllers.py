# -*- coding: utf-8 -*-
from odoo import http

# class AlloyModule(http.Controller):
#     @http.route('/alloy_module/alloy_module/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/alloy_module/alloy_module/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('alloy_module.listing', {
#             'root': '/alloy_module/alloy_module',
#             'objects': http.request.env['alloy_module.alloy_module'].search([]),
#         })

#     @http.route('/alloy_module/alloy_module/objects/<model("alloy_module.alloy_module"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('alloy_module.object', {
#             'object': obj
#         })