# See LICENSE file for full copyright and licensing details.

{
    "name": "Bulk invoice",
    "version": "1.0",
    "author": "Gracias Kasongo",
    "category": "Account",
    "license": "LGPL-3",
    "summary": "Create bulk invoice",
    "website": "https://gracias.zeslap.com/",
    "depends": ["account", "base"],
    "data": [
        "views/actions.xml",
        "reports/bulk_invoice_report.xml",
        "reports/bulk_invoice_template.xml",
        "reports/bulk_invoice_template2.xml",
        "data/bulk_invoice_seq.xml",
    ],
    "installable": True,
}
