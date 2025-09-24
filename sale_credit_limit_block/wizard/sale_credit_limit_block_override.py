# -*- coding: utf-8 -*-
# License LGPL-3 or later

from odoo import api, fields, models, _


class SaleCreditLimitOverrideWizard(models.TransientModel):
    """Wizard to ask for confirmation when a manager overrides a credit limit."""
    _name = 'sale.credit.limit.override.wizard'
    _description = 'Sale Credit Limit Override Wizard'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order", readonly=True)
    message = fields.Text(string="Confirmation Message", readonly=True)

    def action_confirm_override(self):
        """
        Proceed to confirm the original sale order, bypassing the credit check.
        """
        self.ensure_one()
        return self.sale_order_id.with_context(
            credit_limit_override_approved=True
        ).action_confirm()