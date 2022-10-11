# -*- coding: utf-8 -*-
# License MIT (https://opensource.org/licenses/MIT).

import copy
import logging

import pytz
from pytz import timezone

from odoo import api, fields, models
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    pos_credit_update_ids = fields.One2many(
        "pos.credit.update",
        "account_bank_statement_id",
        string="Non-Accounting Transactions",
    )
    pos_credit_update_balance = fields.Monetary(
        compute="_compute_credit_balance",
        string="Non-Accounting Transactions (Balance)",
        store=True,
    )

    @api.depends("pos_credit_update_ids", "pos_credit_update_ids.balance")
    def _compute_credit_balance(self):
        for st in self:
            st.pos_credit_update_balance = -sum(
                [credit_update.balance for credit_update in st.pos_credit_update_ids]
            )
