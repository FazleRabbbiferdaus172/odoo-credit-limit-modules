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
        # 'security/ir.model.access.csv',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
