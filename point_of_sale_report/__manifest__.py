# -*- coding: utf-8 -*-
{
    'name': "POS Report Category Wise",

    'summary': """Point of sale Report based on POS category
   """,

    'description': """
       POS Report by POS category
    """,

    'author': "HAK Solutions",
    'website': "Hunainfast@gmail.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Point of sale',
    'version': '0.1',
    'license': "AGPL-3",

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],

    'demo': [
        'demo/demo.xml',
    ],
    'images': ['static/description/icon.png'],


    'installable': True,
}

