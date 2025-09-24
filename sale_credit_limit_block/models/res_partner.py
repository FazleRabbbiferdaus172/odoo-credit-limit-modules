# -*- coding: utf-8 -*-

from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_overdue_amount(self):
        self.ensure_one()
        overdue_invoice_domain = [
            ('state', 'not in', ('cancel', 'draft')),
            ('move_type', '=', 'out_invoice'),
            ('payment_state', 'not in', ('in_payment', 'paid', 'reversed', 'blocked', 'invoicing_legacy')),
            ('invoice_date_due', '<', fields.Date.today()),
            ('partner_id', '=', self.id),
        ]
        overdue_invoices = self.env['account.move'].sudo().search(overdue_invoice_domain)
        overdue_amount = sum(overdue_invoices.mapped('amount_residual'))
        return overdue_amount