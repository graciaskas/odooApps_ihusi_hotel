# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Hotel partner book',
    'version': '1.0',
    "description": "Hotel guest partner book",
    "summary": "Report Hotel partner",
    "category": "Human resources",
    "sequence": 20,
    'license': 'LGPL-3',
    "author": "Kas Gracias Tmb",
    'depends': ['base', 'hotel'],
    'data': [
        'views/views.xml',
        'reports/reports.xml',
        'reports/partner_book.xml'
    ],
    'website': 'https://zeslap.com',
    'installable': True,
    'application': True,
}
