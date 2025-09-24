# -*- coding: utf-8 -*-
{
    'name': "Sale Credit Limit Block",

    'summary': "This module blocks confirming sale order when customer has passed credit limit",

    'description': """
                This module blocks confirming sale order when customer has passed credit limit.
    """,

    'author': "Fazle Rabbi Ferdaus",

    'category': 'Sales Management',
    'version': '18.0.1.0.0',

    'depends': ['sale_management', 'contacts'],

    'data': [
        'security/sale_credit_limit_security.xml',
        'security/ir.model.access.csv',
        "wizard/sale_credit_limit_override_wizard_views.xml",
    ],
    'installable': True,
    'license': 'LGPL-3',
}
