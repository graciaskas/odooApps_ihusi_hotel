# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from . import models
from . import reports
from . import wizard
from . import controllers
from .hooks import post_init_hook
from odoo import api, fields, SUPERUSER_ID, _


def _uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    xml_ids = [
        'sale.sale_order_personal_rule',
        'sale.sale_order_see_all',
        'account.account_move_see_all',
        'sale.account_move_personal_rule',
        'sale.account_move_see_all',
        'sale.account_move_line_personal_rule',
        'sale.account_move_line_see_all',
        'purchase.purchase_user_account_move_line_rule',
        'purchase.purchase_user_account_move_rule'
    ]
    for xml_id in xml_ids:
        act_window = env.ref(xml_id, raise_if_not_found=False)
        if xml_id == 'sale.sale_order_personal_rule':
        	act_window.domain_force = "['|',('user_id','=',user.id),('user_id','=',False)]"
        if xml_id == 'sale.sale_order_see_all':
        	act_window.domain_force = "[(1,'=',1)]"
        if xml_id == 'account.account_move_see_all':
        	act_window.domain_force = "[(1, '=', 1)]"
        if xml_id == 'sale.account_move_personal_rule':
        	act_window.domain_force = "[('type', 'in', ('out_invoice', 'out_refund')), '|', ('invoice_user_id', '=', user.id), ('invoice_user_id', '=', False)]"
        if xml_id == 'sale.account_move_see_all':
        	act_window.domain_force = "[('type', 'in', ('out_invoice', 'out_refund'))]"
        if xml_id == 'sale.account_move_line_personal_rule':
        	act_window.domain_force = "[('move_id.type', 'in', ('out_invoice', 'out_refund')), '|', ('move_id.invoice_user_id', '=', user.id), ('move_id.invoice_user_id', '=', False)]"
        if xml_id == 'sale.account_move_line_see_all':
        	act_window.domain_force = "[('move_id.type', 'in', ('out_invoice', 'out_refund'))]"
        if xml_id == 'purchase.purchase_user_account_move_line_rule':
        	act_window.domain_force = "[('move_id.type', 'in', ('in_invoice', 'in_refund', 'in_receipt'))]"
        if xml_id == 'purchase.purchas"e_user_account_move_rule':
        	act_window.domain_force = "[('type', 'in', ('in_invoice', 'in_refund', 'in_receipt'))]"

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
