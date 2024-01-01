# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Estate",  # The name that will appear in the App list
    "version": "1.0.0",  # Version
    'category': 'Estate',
        'sequence': -2,
        'summary': 'Estate',
        'description': """
            Estate
        """,
    "depends": ["base"],  # dependencies
    "data": [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
        'views/res_users_views.xml',
        'views/estate_menus.xml'
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    'license': 'LGPL-3',
}
