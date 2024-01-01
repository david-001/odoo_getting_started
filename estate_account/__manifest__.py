# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Estate Account",  # The name that will appear in the App list
    "version": "1.0.0",  # Version
    'category': 'Estate Account',
        'sequence': -1,
        'summary': 'Estate Account',
        'description': """
            Estate Account
        """,
     "depends": [
         "estate",
        "account",
     ],
    "installable": True,
    "application": True,
    "auto_install": False,
    'license': 'LGPL-3',
}
