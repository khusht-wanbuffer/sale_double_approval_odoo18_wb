# -*- coding: utf-8 -*-
# from odoo import http


# class StudentReg(http.Controller):
#     @http.route('/student__reg/student__reg', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/student__reg/student__reg/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('student__reg.listing', {
#             'root': '/student__reg/student__reg',
#             'objects': http.request.env['student__reg.student__reg'].search([]),
#         })

#     @http.route('/student__reg/student__reg/objects/<model("student__reg.student__reg"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('student__reg.object', {
#             'object': obj
#         })

