# -*- coding: utf-8 -*-
"""Sale Model for Custom Credit Limit."""
from odoo import models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    """Inherit Sale Order to add credit limit validation."""
    _inherit = 'sale.order'

    @staticmethod
    def calculate_new_overdue(partner, order_amount):
        """Calculate new overdue amount."""
        current_overdue = partner.get_overdue_amount()
        return current_overdue + order_amount

    def _launch_credit_override_wizard(self, message):
        """Create and launch the confirmation wizard."""
        self.ensure_one()
        wizard = self.env['sale.credit.limit.override.wizard'].create({
            'sale_order_id': self.id,
            'message': message,
        })
        return {
            'name': _('Sale Order Confirmation'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.credit.limit.override.wizard',
            'res_id': wizard.id,
            'target': 'new',
        }

    def action_confirm(self):
        """Raise ValidationError or Confirmation wizard based on
        user permission if overdue amount exceeds limit."""

        if self.env.context.get('credit_limit_override_approved'):
            return super().action_confirm()

        if self.env.company.account_use_credit_limit:
            for order in self:
                partner = order.partner_id.sudo()

                if partner.credit_limit > 0:
                    overdue_amount = self.calculate_new_overdue(partner, order.amount_total)

                    if overdue_amount > partner.credit_limit:
                        message = _(
                            "Cannot confirm Sale Order. The customer '%(partner_name)s' has "
                            "exceeded their credit limit.\n\n"
                            "Overdue Amount: %(existing_overdue)s\n"
                            "This Order's Total: %(order_total)s\n"
                            "New Total Receivable: %(new_total)s\n"
                            "Credit Limit: %(credit_limit)s"
                        ) % {
                                      'partner_name': partner.name,
                                      'existing_overdue': overdue_amount - order.amount_total,
                                      'order_total': order.amount_total,
                                      'new_total': overdue_amount,
                                      'credit_limit': partner.credit_limit,
                                  }
                        can_override = self.env.user.has_group('sale_credit_limit_block.group_credit_limit_override')
                        if can_override:
                            return order._launch_credit_override_wizard(message)
                        raise ValidationError(message)

        return super().action_confirm()
