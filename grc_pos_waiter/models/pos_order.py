# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from functools import partial
from datetime import datetime


class PosOrder(models.Model):
    _inherit = 'pos.order'
    waiter_id = fields.Many2one(
        "hr.employee",
        domain="[('is_waiter', '=', True)]",
        string="Waiter",
        help='The Waiter of the order'
    )

    @api.model
    def _order_fields(self, ui_order):
        """In this function the waiter that we defined from the
        pos interface is fetched to the pos order which is created
        in the backend"""

        process_line = partial(self.env['pos.order.line']._order_line_fields)
        return {
            'user_id':      ui_order['user_id'] or False,
            'session_id':   ui_order['pos_session_id'],
            'lines':        [process_line(l) for l in ui_order['lines']] if ui_order['lines'] else False,
            'pos_reference': ui_order['name'],
            'sequence_number': ui_order['sequence_number'],
            'partner_id':   ui_order['partner_id'] or False,
            'date_order':   ui_order['creation_date'].replace('T', ' ')[:19],
            'fiscal_position_id': ui_order['fiscal_position_id'],
            'pricelist_id': ui_order['pricelist_id'],
            'amount_paid':  ui_order['amount_paid'],
            'amount_total':  ui_order['amount_total'],
            'amount_tax':  ui_order['amount_tax'],
            'amount_return':  ui_order['amount_return'],
            'company_id': self.env['pos.session'].browse(ui_order['pos_session_id']).company_id.id,
            'waiter_id': ui_order.get('waiter_id'),
            'to_invoice': ui_order['to_invoice'] if "to_invoice" in ui_order else False,
        }
