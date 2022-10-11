# -*- coding : utf-8 -*-

{
    'name': 'Hotel Management extension',
    'version': '1.0',
    'author': 'Gracias Kasongo',
    'website': 'https://gracias.zeslap.com',
    'description': 'Serpent consulting hotel module extension',
    'summury': """
        This module add some features to the Serpent consulting hotel management module
    """,
    'depends': ['base', 'hotel', 'hotel_reservation', 'sale'],
    'data': [
        'views/hotel_reservation.xml',
        'views/hotel_folio.xml',
        'reports/hotel_folio.xml',
        'reports/hotel_folio_template.xml',
        'reports/report_checkin_reservation.xml',
        'reports/report_checkin_reservation_template.xml',
        'reports/report_confirm_reservation.xml',
        'reports/report_confirm_reservation_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
