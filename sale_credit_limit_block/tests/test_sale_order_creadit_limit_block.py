# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo.fields import Command, Date
from odoo.exceptions import ValidationError
from odoo.addons.sale.tests.common import TestSaleCommon


class TestSaleCreditLimitBlock(TestSaleCommon):
    """
    Test suite for the custom credit limit block functionality on sale order.
    It verifies that sale orders are correctly blocked when a customer's
    credit limit is exceeded by overdue invoices.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.account_use_credit_limit = True

        buck_currency = cls.env['res.currency'].create({
            'name': 'TB',
            'symbol': 'TB',
        })
        cls.env['res.currency.rate'].create({
            'name': '2025-01-01',
            'rate': 2.0,
            'currency_id': buck_currency.id,
            'company_id': cls.env.company.id,
        })

        cls.buck_pricelist = cls.env['product.pricelist'].create({
            'name': 'Test Buck Pricelist',
            'currency_id': buck_currency.id,
        })

        cls.company_data_2 = cls.setup_other_company()

        cls.sales_user = cls.company_data['default_user_salesman']
        cls.sales_user.write({
            'login': "notaccountman",
            'email': "bad@accounting.com",
        })

        cls.empty_order = cls.env['sale.order'].create({
            'partner_id': cls.partner_a.id,
        })

        limit_override_group = cls.env.ref('sale_credit_limit_block.group_credit_limit_override')
        cls.limit_override_user = cls.env['res.users'].create({
            'name': 'Sales Manager',
            'login': 'manager',
            'groups_id': [(6, 0, [limit_override_group.id])]
        })

    def _create_sale_order(self, user, price_unit):
        sale_order = self.env['sale.order'].with_user(user).create(
            {
                'partner_id': self.partner_a.id,
                'partner_invoice_id': self.partner_a.id,
                'partner_shipping_id': self.partner_a.id,
                'pricelist_id': self.company_data['default_pricelist'].id,
                'order_line': [Command.create({
                    'product_id': self.company_data['product_order_no'].id,
                    'price_unit': price_unit,
                })]
            }
        )
        return sale_order

    def _create_invoice(self, price_unit, invoice_date_days=0, due_date_days=0):
        invoice = self.env['account.move'].create({
            'partner_id': self.partner_a.id,
            'move_type': 'out_invoice',
            'invoice_date': Date.today() + timedelta(days=invoice_date_days),
            'invoice_date_due': Date.today() + timedelta(days=due_date_days),
            'invoice_line_ids': [Command.create({
                'product_id': self.company_data['product_order_no'].id,
                'quantity': 1,
                'price_unit': price_unit,
            })],
        })
        return invoice

    def test_confirm_sale_order_below_limit(self):
        self.env.company.account_use_credit_limit = True
        self.partner_a.credit_limit = 1000.0
        sale_order = self._create_sale_order(self.sales_user, 1000)
        sale_order.with_user(self.sales_user).action_confirm()
        self.assertEqual(sale_order.state, "sale")

    def test_block_sale_order_exceeding_limit(self):
        self.env.company.account_use_credit_limit = True
        self.partner_a.credit_limit = 1000.0
        sale_order = self._create_sale_order(self.sales_user, 1001)

        with self.assertRaises(ValidationError):
            sale_order.with_user(self.sales_user).action_confirm()
            self.assertNotEqual(sale_order.state, "sale")

    def test_amount_overdue_ignores_invoices_that_do_not_pass_due_date_from_payment_term(self):
        invoice = self._create_invoice(1000, 0, 365)
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")
        amount_overdue = self.partner_a.get_overdue_amount()
        self.assertEqual(amount_overdue, 0)

    def test_amount_overdue_includes_invoices_that_pass_due_date_from_payment_term(self):
        invoice = self._create_invoice(1000, -2, -1)
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")
        amount_overdue = self.partner_a.get_overdue_amount()
        self.assertEqual(amount_overdue, 1000)

    def test_amount_overdue_ignores_draft_invoices(self):
        invoice = self._create_invoice(1000, -2, -1)
        self.assertEqual(invoice.state, "draft")
        amount_overdue = self.partner_a.get_overdue_amount()
        self.assertEqual(amount_overdue, 0)

    def test_amount_overdue_ignores_canceled_invoices(self):
        invoice = self._create_invoice(1000, -2, -1)
        invoice.button_cancel()
        self.assertEqual(invoice.state, "cancel")
        amount_overdue = self.partner_a.get_overdue_amount()
        self.assertEqual(amount_overdue, 0)

    def test_amount_overdue_includes_not_paid_and_partial_paid_invoices(self):
        def register_payment_and_assert_state(move, amount):
            self.env['account.payment.register'].with_context(
                active_model='account.move',
                active_ids=move.ids
            ).create({'amount': amount})._create_payments()

        invoice_paid = self._create_invoice(1000, -2, -1)

        invoice_paid.action_post()
        register_payment_and_assert_state(invoice_paid, 1000.0)
        self.assertEqual(invoice_paid.payment_state, "paid")
        amount_overdue = self.partner_a.get_overdue_amount()
        self.assertEqual(amount_overdue, 0)

        invoice_partially_paid = self._create_invoice(1000, -2, -1)

        invoice_partially_paid.action_post()
        register_payment_and_assert_state(invoice_partially_paid, 500.0)
        self.assertEqual(invoice_partially_paid.payment_state, "partial")
        amount_overdue = self.partner_a.get_overdue_amount()
        self.assertEqual(amount_overdue, 500)

        invoice_not_paid = self._create_invoice(500, -2, -1)

        invoice_not_paid.action_post()
        self.assertEqual(invoice_not_paid.payment_state, "not_paid")
        amount_overdue = self.partner_a.get_overdue_amount()
        self.assertEqual(amount_overdue, 1000)

    def test_user_with_group_credit_limit_override_gets_wizard_on_exceed(self):
        self.env.company.account_use_credit_limit = True
        self.partner_a.credit_limit = 1000.0
        sale_order = self._create_sale_order(self.limit_override_user, 1001)
        action = sale_order.with_user(self.limit_override_user).action_confirm()

        self.assertIsInstance(action, dict, "Manager should receive an action dictionary.")
        self.assertEqual(action.get('type'), 'ir.actions.act_window')
        self.assertEqual(action.get('res_model'), 'sale.credit.limit.override.wizard')
        self.assertEqual(sale_order.state, 'draft')

    def test_credit_limit_block_bypass(self):
        self.env.company.account_use_credit_limit = True
        self.partner_a.credit_limit = 1000.0
        sale_order = self._create_sale_order(self.sales_user, 1001)
        with self.assertRaises(ValidationError):
            sale_order.action_confirm()
            self.assertEqual(sale_order.state, 'draft')
        sale_order.with_context(credit_limit_override_approved=True).action_confirm()
        self.assertEqual(sale_order.state, 'sale')
