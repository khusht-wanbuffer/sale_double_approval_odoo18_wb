# -- coding: utf-8 --
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Wan Buffer Solution (<https://wanbuffer.com/>).
#
#    For Module Support : info@wanbuffer.com  or Call : +91 9638442270
#
##############################################################################

from odoo import api, fields, models
from odoo.exceptions import ValidationError

from ast import literal_eval

class ResConfigSettings(models.TransientModel):
    """ Inheriting the settings to add custom fields """
    _inherit = 'res.config.settings'

    so_approval = fields.Boolean(
        string="Sale Order Approval",
        help="Enable this option to require double validation for sale orders."
    )
    
    # Row 1 Fields
    so_min_amount = fields.Monetary(
        string="Minimum Amount",
        help="Specify the minimum amount that triggers the double validation "
             "for sale orders. Sale orders exceeding this amount will require "
             "approval by a sales manager."
    )
    so_max_amount = fields.Monetary(
        string="Maximum Amount",
        help="Specify the maximum amount that triggers the double validation "
             "for sale orders. Sale orders exceeding this amount will require "
             "approval by a sales manager."
    )
    approval = fields.Many2one(
        "res.users",
        string="Approval",
        help="Select the user who will be responsible for approving sale orders",
        domain="[('share', '=', False)]"
    )
    
    # Row 2 Fields
    so_min_amount2 = fields.Monetary(
        string="Minimum Amount 2",
        help="Specify the minimum amount that triggers the double validation "
             "for sale orders. Sale orders exceeding this amount will require "
             "approval by a sales manager."
    )
    so_max_amount2 = fields.Monetary(
        string="Maximum Amount 2",
        help="Specify the maximum amount that triggers the double validation "
             "for sale orders. Sale orders exceeding this amount will require "
             "approval by a sales manager."
    )
    approval2 = fields.Many2one(
        "res.users",
        string="Approval 2",
        help="Select the user who will be responsible for approving sale orders",
        domain="[('share', '=', False)]"
    )

    
    # Row 3 Fields
    so_min_amount3 = fields.Monetary(
        string="Minimum Amount 3",
        help="Specify the minimum amount that triggers the double validation "
             "for sale orders. Sale orders exceeding this amount will require "
             "approval by a sales manager."
    )
    approval3 = fields.Many2one(
        "res.users",
        string="Approval 3",
        help="Select the user who will be responsible for approving sale orders",
        domain="[('share', '=', False)]"
    )
    map_box_token = fields.Char(
        string="Mapbox Token",
        help="Enter your Mapbox API token here."
    )

    @api.constrains('so_min_amount', 'so_max_amount', 'so_min_amount2', 
                    'so_max_amount2', 'so_min_amount3' )
    def _check_amount_ranges(self):
        """Validate that ranges don't overlap and are logical"""
        for record in self:
            if record.so_min_amount >= record.so_max_amount:
                raise ValidationError("Range 1: Minimum amount must be less than maximum amount")

            if record.so_min_amount2 and record.so_min_amount2 <= record.so_max_amount:
                raise ValidationError("Range 2: Minimum amount must be greater than Range 1 maximum")

            if record.so_max_amount2 and record.so_min_amount2 >= record.so_max_amount2:
                raise ValidationError("Range 2: Minimum amount must be less than maximum amount")

            if record.so_min_amount3 and record.so_min_amount3 <= record.so_max_amount2:
                raise ValidationError("Range 3: Minimum amount must be greater than Range 2 maximum")
 
    @api.model
    def get_values(self):
        """ Override to get the values of the custom fields from the
        'ir.config_parameter' model. """
        res = super(ResConfigSettings, self).get_values()
        icp_sudo = self.env['ir.config_parameter'].sudo()
        
        # Get Boolean and Float/Monetary values
        res.update({
            'so_approval': icp_sudo.get_param(
                "sales_double_approval.so_approval", default=False),
            
            # Row 1 Values
            'so_min_amount': float(icp_sudo.get_param(
                "sales_double_approval.so_min_amount", default=0.0)),
            'so_max_amount': float(icp_sudo.get_param(
                "sales_double_approval.so_max_amount", default=0.0)),
            
            # Row 2 Values
            'so_min_amount2': float(icp_sudo.get_param(
                "sales_double_approval.so_min_amount2", default=0.0)),
            'so_max_amount2': float(icp_sudo.get_param(
                "sales_double_approval.so_max_amount2", default=0.0)),
            
            # Row 3 Values
            'so_min_amount3': float(icp_sudo.get_param(
                "sales_double_approval.so_min_amount3", default=0.0)),
        })
        
        # Get Many2one values (User IDs)
        approval_id = icp_sudo.get_param(
            "sales_double_approval.approval", default=False)
        if approval_id:
            res['approval'] = int(approval_id)
        
        approval2_id = icp_sudo.get_param(
            "sales_double_approval.approval2", default=False)
        if approval2_id:
            res['approval2'] = int(approval2_id)
            
        approval3_id = icp_sudo.get_param(
            "sales_double_approval.approval3", default=False)
        if approval3_id:
            res['approval3'] = int(approval3_id)
        
        return res

    @api.model
    def set_values(self):
        """ Override to set the values of the custom fields in the
        'ir.config_parameter' model. """
        super(ResConfigSettings, self).set_values()
        icp_sudo = self.env['ir.config_parameter'].sudo()
        
        # Set Boolean and Float/Monetary values
        icp_sudo.set_param( 
            "sales_double_approval.so_approval",
            self.so_approval)
        
        # Row 1 Values
        icp_sudo.set_param(
            "sales_double_approval.so_min_amount",
            self.so_min_amount or 0.0)
        icp_sudo.set_param(
            "sales_double_approval.so_max_amount",
            self.so_max_amount or 0.0)
        
        # Row 2 Values   
        icp_sudo.set_param(
            "sales_double_approval.so_min_amount2",
            self.so_min_amount2 or 0.0)
        icp_sudo.set_param(
            "sales_double_approval.so_max_amount2",
            self.so_max_amount2 or 0.0)
        
        # Row 3 Values
        icp_sudo.set_param(
            "sales_double_approval.so_min_amount3",
            self.so_min_amount3 or 0.0)
    
        
        # Set Many2one values (User IDs)
        icp_sudo.set_param(
            "sales_double_approval.approval",
            self.approval.id if self.approval else False)
        icp_sudo.set_param(
            "sales_double_approval.approval2",
            self.approval2.id if self.approval2 else False)
        icp_sudo.set_param(
            "sales_double_approval.approval3",
            self.approval3.id if self.approval3 else False)


