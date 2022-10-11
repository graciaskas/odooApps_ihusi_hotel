# _*_ conding: utf-8 _*_

{
    "name": "Hotel guest PoS",
    "version": "1.0",
    "description": "Unable hotel guest in Pos",
    "summary": "Unable hotel guest in Pos",
    "category": "Point Of Sale",
    "sequence": 20,
    'license': 'LGPL-3',
    "author": "Gracias Kasongo",
    "website": "https//gracias.zeslap.com",
    "depends": ["base", "point_of_sale", "hotel"],
    "data": [
        'views/grc_hotel_pos.xml',
        'views/pos_order.xml',
        # 'views/hotel_folio.xml'
    ],
    "qweb": ['static/src/xml/grc_hotel_pos.xml'],
    "installable": True,
    "application": True,
    "auto_install": False,
    "maintainer": "graciaskas96@gmail.com",
    "support": "graciaskas96@gmail.com",
    'images': [],
}
