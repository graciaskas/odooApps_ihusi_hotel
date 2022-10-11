# _*_ conding: utf-8 _*_

{
    "name": "POS Waiter",
    "version": "1.0",
    "description": "Add a waiter on pos order and ticket",
    "summary": "Add a waiter on pos order and ticket",
    "category": "Point Of Sale",
    "sequence": 20,
    'license': 'OPL-1',
    "author": "Gracias Kasongo",
    "website": "https//gracias.zeslap.com",
    "depends": ["base", "point_of_sale", "hr", "hr_payroll_community"],
    "data": [
        'security/ir.model.access.csv',
        'views/grc_pos_view.xml', 'views/hr_employee.xml', 'views/pos_order.xml', 'views/pos_waiter.xml'],
    "qweb": ['static/src/xml/waiter.xml'],
    "installable": True,
    "application": True,
    "auto_install": False,
    "maintainer": "<graciaskas96@gmail.com",
    "support": "<graciaskas96@gmail.com",
    "price": 25,
    'images': ['images/icon_screenshot.png'],
    "currency": "USD"
}
