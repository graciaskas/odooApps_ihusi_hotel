
{
    'name': 'Pos Quotations',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'sequence': 6,
    'license': 'LGPL-3',
    'summary': 'Create Quotation, Save Quotation and Load Quotation Order in Point Of Sale (Pos). Pos order Pos Note for quotation order',
    'description': """
        pos quotation,
        pos_quotation,
        pos load quotation,
        pos save quotation,
        pos create quotation,
        pos order,
        pos_order_quotation,
        pos_order,
        POS Quotation,
        pos load order,
        POS Quotations,
        point of sale,
        pos save quotation,
        pos load quotation,
        pos order quotation,
        AB Tech,
        Quotation,
        Quotations,
        pos,
        pos_order_quotation,
        pos_load_quotation,
        pos_save_quotation,
        """,
    'author': "AB Tech",
    'website': 'abtechsolution.in',
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/assests.xml',
        'views/pos_quotation.xml',
        'data/ir_sequence.xml',
        'views/pos_order.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
        'static/src/xml/SaveQuotationPopUp.xml',
        'static/src/xml/LoadQuotationPopup.xml',
        'static/src/xml/OrderReceipt.xml',
        'static/src/xml/AlertPopups.xml',
    ],
    "images": ["static/description/banner.gif"],
    'installable': True,
}
