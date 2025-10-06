# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Wan Buffer Solution (<https://wanbuffer.com/>).
#
#    For Module Support : info@wanbuffer.com or Call : +91 9638442270
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    """Inheriting sale.order to add approval workflow"""
    _inherit = 'sale.order'
    
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('to_approve', 'To Approve'),         
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    
    approval_required = fields.Boolean(
        string="Approval Required", 
        compute="_compute_approval_required",
        help="Indicates if this order requires approval based on amount ranges"
    )
    
    approval_level = fields.Char(
        string="Approval Level", 
        compute="_compute_approval_required",
        help="Shows which approval range this order falls into"
    )
    
    can_approve = fields.Boolean(
        string="Can Approve", 
        compute="_compute_can_approve",
        help="Indicates if current user can approve this order"
    )
    
    
    def _get_approval_ranges(self):
        """Get all approval ranges configuration - FIXED: No object caching"""
        get_param = self.env['ir.config_parameter'].sudo().get_param
        
        return {
            'range1': {
                'min': float(get_param('sales_double_approval.so_min_amount', default=0.0)),
                'max': float(get_param('sales_double_approval.so_max_amount', default=1000.0)),
                'approver': get_param('sales_double_approval.approval'),
                'name': 'Range 1'
            },
            'range2': {
                'min': float(get_param('sales_double_approval.so_min_amount2', default=1001.0)),
                'max': float(get_param('sales_double_approval.so_max_amount2', default=5000.0)),
                'approver': get_param('sales_double_approval.approval2'),
                'name': 'Range 2'
            },
            'range3': {
                'min': float(get_param('sales_double_approval.so_min_amount3', default=5001.0)),
                'max': None,  # last range is open-ended
                'approver': get_param('sales_double_approval.approval3'),
                'name': 'Range 3'
            }
        }


    def _get_amount_range_info(self, amount):
        """Get range information for given amount"""
        ranges = self._get_approval_ranges()

        # check normal ranges
        for range_key, range_config in ranges.items():
            min_amt = range_config['min']
            max_amt = range_config['max']
            range_name = range_config['name']
            approver = range_config['approver']

            # last range (open-ended)
            if max_amt is None and amount >= min_amt:
                return {
                    'required': True,
                    'level': f"{range_name} (>= {min_amt})",
                    'approver': approver
                }

            # normal ranges
            if max_amt is not None and min_amt <= amount <= max_amt:
                return {
                    'required': True,
                    'level': f"{range_name} ({min_amt}-{max_amt})",
                    'approver': approver
                }

        # if no range matches
        return {'required': False, 'level': '', 'approver': None}
    
    @api.depends('amount_total')
    def _compute_approval_required(self):
        """Check if amount falls within any of the configured approval ranges,
        ignoring ranges with 0 values."""
        for order in self:
            ranges = order._get_approval_ranges()
            is_in_range = False
            range_level = ""

            for range_key, range_config in ranges.items():
                min_amt = range_config['min']
                max_amt = range_config['max']
                range_name = range_config['name']

                # Skip invalid/unset ranges (0 or None)
                if not min_amt and not max_amt:
                    continue

                if max_amt is None:  # open-ended range
                    if order.amount_total >= min_amt:
                        is_in_range = True
                        range_level = f"{range_name} (>= {min_amt})"
                        break
                else:  # closed range
                    if min_amt <= order.amount_total <= max_amt:
                        is_in_range = True
                        range_level = f"{range_name} ({min_amt} - {max_amt})"
                        break

            order.approval_required = is_in_range
            order.approval_level = range_level


    # @api.depends('amount_total')
    # def _compute_approval_required(self):
    #     """Check if amount falls within any of the three approval ranges"""
    #     for order in self:
    #         # Get all ranges configuration
    #         ranges = order._get_approval_ranges()
    #         is_in_range = False
    #         range_level = ""

    #         # Check each range
    #         for range_key, range_config in ranges.items():
    #             min_amt = range_config['min']
    #             max_amt = range_config['max']
    #             range_name = range_config['name']

    #             # Check if amount falls in current range
    #             if max_amt is None:  # For Range 3 (open-ended)
    #                 if order.amount_total >= min_amt:
    #                     is_in_range = True
    #                     range_level = f"{range_name} (>= {min_amt})"
    #                     break
    #             else:  # For Range 1 and 2
    #                 if min_amt <= order.amount_total <= max_amt:
    #                     is_in_range = True
    #                     range_level = f"{range_name} ({min_amt} - {max_amt})"
    #                     break

    #         order.approval_required = is_in_range
    #         order.approval_level = range_level

    
    @api.depends('amount_total', 'approval_level')
    def _compute_can_approve(self):
        """Check if current user can approve based on amount range - FIXED"""
        current_user_id = self.env.user.id
        is_sales_manager = self.env.user.has_group('sales_team.group_sale_manager')
        
        for order in self:
            if not order.approval_required:
                order.can_approve = True
                continue
            
            range_info = order._get_amount_range_info(order.amount_total)
            approver_id = range_info.get('approver')
            
            can_approve = False
            if approver_id:
                try:
                    if int(approver_id) == current_user_id:
                        can_approve = True
                except (ValueError, TypeError):
                    pass
            
            # Fallback: Sales manager can always approve
            if not can_approve and is_sales_manager:
                can_approve = True
                
            order.can_approve = can_approve

    
    def action_confirm(self):
        """Override to add approval logic"""
        for order in self:
            # Check if approval is enabled and required
            if order.approval_required and order.state == 'draft':
                # Set to approval state instead of confirming
                order.write({'state': 'to_approve'})
                
                # Send notification to approver
                order.create_approval_activity()
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Approval Required'),
                        'message': _('Order %s requires approval. Amount: %s', order.name, order.amount_total),
                        'type': 'warning'
                    }
                }
        
        # If no approval required or already approved, confirm normally
        return super().action_confirm()

    def button_approve(self):
        """Method to approve the sale order and send email"""
        for order in self:
            if not order.can_approve:
                raise UserError(_("You don't have permission to approve this order."))
            
            # Approve and confirm the order
            order.write({'state': 'sent'})

            
            return True

    def action_cancel(self):
        """Method to cancel the sale order"""
        self.write({'state': 'cancel'})
        return True

    @api.model
    def create_approval_activity(self, order_id, approver_id):
        """Create single approval activity - prevents duplicates"""
        order = self.browse(order_id)
        approver = self.env['res.users'].browse(approver_id)
        
        # Check for existing activities
        domain = [
            ('res_id', '=', order_id),
            ('res_model', '=', 'sale.order'),
            ('user_id', '=', approver_id),
            ('activity_type_id.name', '=', 'Email'),
            ('summary', 'ilike', f'approve%{order.name}%')
        ]
        
        existing = self.env['mail.activity'].search(domain, limit=1)
        
        if not existing:
            # Create new activity
            self.env['mail.activity'].create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_email').id,
                'user_id': approver_id,
                'res_id': order_id,
                'res_model': 'sale.order',
                'summary': f'Approve Sale Order {order.name}',
                'note': f'Please approve order {order.name} for {order.currency_id.symbol}{order.amount_total}'
            })
        
        return existing.id if existing else True


    def action_sent_for_approval(self):
        """Send for approval with EMAIL activity (not To-Do)"""
        for order in self:
            if order.state != 'draft':
                raise UserError(_("Only draft quotations can be sent for approval."))
            if not order.approval_required:
                raise UserError(_("This quotation does not require approval."))
            
            # Change state
            order.write({'state': 'to_approve'})
            
            # Get approver
            approver = order._get_approver_user()
            
            if approver:
                # Use default Odoo EMAIL activity type (not To-Do)
                order.activity_schedule(
                    'mail.mail_activity_data_email',  # Default EMAIL activity
                    user_id=approver.id,
                    summary=_('Approve Sale Order %s', order.name),
                    note=_(
                        'Sale Order Approval Required\n\n'
                        'Order Number: %s\n'
                        'Customer: %s\n'
                        'Amount: %s%s\n\n'
                        'Please review and approve this order.\n'
                        'Email notification will be sent upon approval.',
                        order.name, order.partner_id.name, 
                        order.currency_id.symbol, order.amount_total
                    )
                )
                
                # Send actual email to approver
                try:
                    mail_template = self.env.ref(
                        'sales_double_approval.email_template_quotation_approval_request',
                        raise_if_not_found=False
                    )
                    if mail_template:
                        mail_template.with_context(approver_id=approver.id).send_mail(
                            order.id, 
                            force_send=True, 
                            email_values={'email_to': approver.email}
                        )
                except Exception:
                    pass  # Fail silently for email issues
            
            return True

    def _get_approver_user(self):
        """Get the appropriate approver based on amount range - FIXED"""
        range_info = self._get_amount_range_info(self.amount_total)
        approver_id = range_info.get('approver')
        
        if approver_id:
            try:
                approver = self.env['res.users'].browse(int(approver_id))
                if approver.exists():
                    return approver
            except (ValueError, TypeError):
                pass
        
        return self.env['res.users']  


