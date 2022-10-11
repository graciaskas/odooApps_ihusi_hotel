# -*-coding: utf-8 -*-
{
    'name': "Stock Report",
    'summary': "Help you to have a printed PDF document of a stock.",
    'description': """
        Report a stock for a location. This module
        will give you the in, out and the balance of location between
        a period and the details if requested.
    """,
    'author': "Gracias Kasongo",
    'website': "http://gracias.zeslap.com",
    'category': 'Inventory',
    'version': '1.0',
    'licence': 'LGPL-3',
    'depends': ['stock', 'web', 'base'],
    'data': [
        'reports/stock_report.xml',
        'reports/stock_report_details.xml',
        'wizards/stock_report_wizard.xml'
    ],
    'demo': [],
    'installable': True,
    'currency': 'USD',
    'images': ['static/images/main_screenshot.png']
}
