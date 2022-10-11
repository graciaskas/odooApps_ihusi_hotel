# -*- coding: utf-8 -*-
# License MIT (https://opensource.org/licenses/MIT).

import copy
import logging

import pytz
from pytz import timezone

from odoo import api, fields, models
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = "account.journal"

    debt = fields.Boolean(string="Credit Journal")
    pos_cash_out = fields.Boolean(
        string="Allow to cash out credits",
        default=False,
        help="Partner can exchange credits to cash in POS",
    )
    category_ids = fields.Many2many(
        "pos.category",
        string="POS product categories",
        help="POS product categories that can be paid with this credits."
        "If the field is empty then all categories may be purchased with this journal",
    )
    debt_limit = fields.Float(
        string="Max Debt",
        digits="Account",
        default=0,
        help="Partners is not allowed to have a debt more than this value",
    )
    credits_via_discount = fields.Boolean(
        default=False,
        string="Zero transactions on credit payments",
        help="Discount the order (mostly 100%) when user pay via this type of credits",
    )
    credits_autopay = fields.Boolean(
        "Autopay",
        default=False,
        help="On payment screen it will be automatically used if balance is positive. "
        "In case of several autopay journals they will be applied in Journal order until full amount is paid",
    )

    @api.onchange("credits_via_discount")
    def _onchange_partner(self):
        if self.credits_via_discount is True:
            self.pos_cash_out = False
