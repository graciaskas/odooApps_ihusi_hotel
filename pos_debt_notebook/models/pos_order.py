# -*- coding: utf-8 -*-
# License MIT (https://opensource.org/licenses/MIT).

import copy
import logging

import pytz
from pytz import timezone

from odoo import api, fields, models, _
from odoo.tools import float_is_zero
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    product_list = fields.Text(
        "Product list", compute="_compute_product_list", store=True
    )
    pos_credit_update_ids = fields.One2many(
        "pos.credit.update", "order_id", string="Non-Accounting Payments"
    )
    amount_via_discount = fields.Float(
        "Amount via Discounts", help="Service field for proper order proceeding"
    )

    @api.depends(
        "lines",
        "lines.product_id",
        "lines.product_id.name",
        "lines.qty",
        "lines.price_unit",
    )
    def _compute_product_list(self):
        for order in self:
            product_list = list()
            for o_line in order.lines:
                product_list.append(
                    "%s(%s * %s)"
                    % (o_line.product_id.name, o_line.qty, o_line.price_unit)
                )
            order.product_list = " + ".join(product_list)

    @api.model
    def _process_order(self, order, draft, existing_order):
        # Don't change original dict, because in case of SERIALIZATION_FAILURE
        # the method will be called again
        order = copy.deepcopy(order)
        pos_order = order["data"]
        # covert creation_date o time format string
        pos_order.update({
            'creation_date': pos_order['creation_date'].replace('T', ' ')[:19]
        })
        # covert creation_date to time format string
        order.update({
            'creation_date': pos_order['creation_date'].replace('T', ' ')[:19]
        })
        credit_updates = []
        amount_via_discount = 0

        for payment in pos_order["statement_ids"]:
            pm = self.env["pos.payment.method"].browse(
                payment[2]["payment_method_id"])
            if pm.is_cash_count and pm.cash_journal_id and pm.cash_journal_id.debt:
                amount = float(payment[2]["amount"])
                product_list = list()
                amount_via_discount += amount
                for o_line in pos_order["lines"]:
                    o_line = o_line[2]
                    name = self.env["product.product"].browse(
                        o_line["product_id"]).name
                    product_list.append(
                        "{}({} * {})".format(name,
                                             o_line["qty"], o_line["price_unit"])
                    )
                product_list = " + ".join(product_list)
                credit_updates.append(
                    {
                        "journal_id": pm.cash_journal_id.id,
                        "balance": -amount,
                        "partner_id": pos_order["partner_id"],
                        "update_type": "balance_update",
                        "note": product_list,
                    }
                )
                payment[2]["amount"] = 0
        pos_order["amount_via_discount"] = amount_via_discount
        order_id = super(PosOrder, self)._process_order(
            order, draft, existing_order)
        for update in credit_updates:
            update["order_id"] = order_id
            entry = self.env["pos.credit.update"].sudo().create(update)
            entry.switch_to_confirm()
        self.browse(order_id).set_discounts()
        return order_id

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res["amount_via_discount"] = ui_order.get("amount_via_discount", 0)
        return res

    def set_discounts(self):
        amount = self.amount_via_discount
        for line in self.lines:
            if float_is_zero(
                amount, self.env["decimal.precision"].precision_get("Account")
            ):
                break
            price = line.price_subtotal_incl
            if not price:
                continue
            disc = line.discount
            line.write(
                {
                    "discount": disc
                    # "discount": disc == 100
                    # and disc
                    # or max(
                    #     min(
                    #         line.discount
                    #         + (
                    #             amount
                    #             / (disc and (price / (100 - disc)) * 100 or price)
                    #         )
                    #         * 100,
                    #         100,
                    #     ),
                    #     0,
                    # ),
                }
            )
            # since 12.0v methods used api.depends in 11.0 use api.onchange, so we need to update some fields manually
            line._onchange_amount_line_all()
            amount -= price - line.price_subtotal_incl
        # since 12.0v methods used api.depends in 11.0 use api.onchange, so we need to update some fields manually
        self._onchange_amount_all()
        return amount

    def _is_pos_order_paid(self):
        return super(PosOrder, self)._is_pos_order_paid() or (
            not self.payment_ids and self.amount_via_discount
        )
