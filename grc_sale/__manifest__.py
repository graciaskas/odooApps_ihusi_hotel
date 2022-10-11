# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) ZeSlap Inc (<https://zeslap.com/>).
#
#    For Module Support : graciaskas96@gmail.com
#
##############################################################################
{
    "name": "Sale extension.",
    "version": "1.0",
    "summary": "Sale extension",
    "category": "Sale",
    "license": "LGPL-3",
    "description": """
        This module adds some features to the sale module
    """,
    "author": "Gracias Kasongo",
    "depends": ["base", "sale", "sale_management"],
    "data": [
        'views/sale_order.xml',
        "reports/sale.xml",
        "reports/sale_order_report_template.xml",
    ],
    "demo": [],
    "images": ["static/description/icon.png"],
    "installable": True,
    "application": False,
    "auto_install": False,
    "website": "https//zeslap.com",
}
