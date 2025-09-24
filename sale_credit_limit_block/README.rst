..
=======================
Credit Limit block for Sale Orders
=======================

Block sale order confirmation if customer has passed credit limit. If the user has proper permission a wizard will ask for confimation to bypass the block and then will confirm the sale order if confirm button is clicked.

**Table of contents**

.. contents::
   :local:

Configuration
=============

To configure this module, you need to:

1. Go to *Settings > Invoicing > Customer Invoices*.
2. Check "Sales Credit Limit".
3. Insert value in "Default Credit Limit" feild and save.


Usage
=====

To use this module, you need to:

1. Go to Contacts app.
2. Choose any partner and click on "Invoicing" tab.
3. Check the "Partner Limit" checkbox.
4. If you choose to you can change the credit limit for each partner from here.
5. Go to sale order, confirm any sale order, if the partner has any overdue invoice and the sumation of order amount and overdue amount is greater than credit limit, will raise a validation error and sale order wont be confirmed.
6. Credit limit block can be bypassed with "Override Credit Limit" group permission.
7. When user has "Override Credit Limit" permission, A confimation wizad will popup.
8. Click on "Confirm Sale Order" on the wizard to confirm blocked sale orders.



