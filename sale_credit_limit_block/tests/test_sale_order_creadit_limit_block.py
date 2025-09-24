# -*- coding: utf-8 -*-

from odoo.fields import Command
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

    def test_confirm_sale_order_below_limit(self):
        self.env.company.account_use_credit_limit = True
        self.partner_a.credit_limit = 1000.0
        sale_order_values = {
            'partner_id': self.partner_a.id,
            'partner_invoice_id': self.partner_a.id,
            'partner_shipping_id': self.partner_a.id,
            'pricelist_id': self.company_data['default_pricelist'].id,
            'order_line': [Command.create({
                'product_id': self.company_data['product_order_no'].id,
                'price_unit': 1000.0,
            })]
        }
        sale_order = self.env['sale.order'].create(
            sale_order_values
        )
        sale_order.action_confirm()
        self.assertEqual(sale_order.state, "sale")

    def test_block_sale_order_exceeding_limit(self):
        self.env.company.account_use_credit_limit = True
        self.partner_a.credit_limit = 1000.0
        sale_order_values = {
            'partner_id': self.partner_a.id,
            'partner_invoice_id': self.partner_a.id,
            'partner_shipping_id': self.partner_a.id,
            'pricelist_id': self.company_data['default_pricelist'].id,
            'order_line': [Command.create({
                'product_id': self.company_data['product_order_no'].id,
                'price_unit': 1001.0,
            })]
        }
        sale_order = self.env['sale.order'].create(
            sale_order_values
        )
        sale_order.action_confirm()
        self.assertNotEqual(sale_order.state, "sale")
