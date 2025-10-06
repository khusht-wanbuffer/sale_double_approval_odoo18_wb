# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class student__reg(models.Model):
#     _name = 'student__reg.student__reg'
#     _description = 'student__reg.student__reg'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()

#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('confirmed', 'Confirmed'),
#         ('done', 'Done'),
#         ('cancelled', 'Cancelled')
#     ], string="Status", default='draft')

#     priority = fields.Selection([
#         ('0', 'Low'),
#         ('1', 'Normal'),
#         ('2', 'High')
#     ], string="Priority")

#     partner_id = fields.Many2one('res.partner', string="Customer")
#     line_ids = fields.One2many('sale.order.line', 'order_id', string="Order Lines")
#     tag_ids = fields.Many2many('product.tag', string="Tags")


#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

