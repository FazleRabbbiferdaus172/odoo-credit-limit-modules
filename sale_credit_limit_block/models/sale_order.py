# -*- coding: utf-8 -*-

from odoo import models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @staticmethod
    def calculate_new_overdue(partner, order_amount):
        current_overdue = 0
        return current_overdue + order_amount

    def action_confirm(self):
        if self.env.company.account_use_credit_limit:
            for order in self:
                partner = order.partner_id

                if partner.credit_limit > 0:
                    overdue_amount = self.calculate_new_overdue(partner, order.amount_total)

                    if overdue_amount > partner.credit_limit:
                        message = _(
                            "Cannot confirm Sale Order. The customer '%s' has "
                            "exceeded their credit limit.\n\n"
                            "Overdue Amount: %s\n"
                            "This Order's Total: %s\n"
                            "New Total Receivable: %s\n"
                            "Credit Limit: %s"
                        ) % (
                                      partner.name,
                                      overdue_amount,
                                      order.amount_total,
                                      overdue_amount,
                                      partner.credit_limit
                                  )
                        raise ValidationError(message)

        return super(SaleOrder, self).action_confirm()
