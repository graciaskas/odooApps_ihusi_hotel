# -*- coding: utf-8 -*-
# License MIT (https://opensource.org/licenses/MIT).

import copy
import logging

import pytz
from pytz import timezone

from odoo import api, fields, models
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)


class PosCreditUpdate(models.Model):
    _name = "pos.credit.update"
    _description = "Manual Credit Updates"
    _inherit = ["mail.thread"]
    _order = "id desc"

    partner_id = fields.Many2one(
        "res.partner", string="Partner", required=True, tracking=True
    )
    user_id = fields.Many2one(
        "res.users", string="Salesperson", default=lambda s: s.env.user, readonly=True
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda s: s.env.user.company_id,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda s: s.env.user.company_id.currency_id,
    )
    balance = fields.Monetary(
        "Balance Update",
        tracking=True,
        help="Change of balance. Negative value for purchases without money (debt). Positive for credit payments (prepament or payments for debts).",
    )
    new_balance = fields.Monetary(
        "New Balance", help="Value to set balance to. Used only in Draft state."
    )
    note = fields.Text("Note")
    date = fields.Datetime(
        string="Date", default=fields.Datetime.now, required=True)

    state = fields.Selection(
        [("draft", "Draft"), ("confirm", "Confirmed"), ("cancel", "Canceled")],
        default="draft",
        required=True,
        tracking=True,
    )
    update_type = fields.Selection(
        [("balance_update", "Balance Update"), ("new_balance", "New Balance")],
        default="balance_update",
        required=True,
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Journal",
        required=True,
        domain="[('debt', '=', True)]",
    )
    order_id = fields.Many2one("pos.order", string="POS Order")
    config_id = fields.Many2one(
        related="order_id.config_id", string="POS", store=True)
    account_bank_statement_id = fields.Many2one(
        "account.bank.statement",
        compute="_compute_bank_statement",
        string="Account Bank Statement",
        store=True,
    )
    reversed_balance = fields.Monetary(
        compute="_compute_reversed_balance",
        string="Payments",
        help="Change of balance. Positive value for purchases without money (debt). Negative for credit payments (prepament or payments for debts).",
    )

    @api.depends("order_id", "journal_id")
    def _compute_bank_statement(self):
        for record in self:
            if record.order_id:
                order = record.env["pos.order"].browse(record.order_id.id)
                record.account_bank_statement_id = (
                    record.env["account.bank.statement"]
                    .search(
                        [
                            ("journal_id", "=", record.journal_id.id),
                            ("pos_session_id", "=", order.session_id.id),
                        ]
                    )
                    .id
                )

    @api.depends("balance")
    def _compute_reversed_balance(self):
        for record in self:
            record.reversed_balance = -record.balance

    def get_balance(self, balance, new_balance):
        return -balance + new_balance

    def update_balance(self, vals):
        partner = (
            vals.get("partner_id")
            and self.env["res.partner"].browse(vals.get("partner_id"))
            or self.partner_id
        )
        new_balance = vals.get("new_balance", self.new_balance)
        state = vals.get("state", self.state) or "draft"
        update_type = vals.get("update_type", self.update_type)
        if state == "draft" and update_type == "new_balance":
            data = partner._compute_partner_journal_debt(self.journal_id.id)
            credit_balance = data[partner.id].get("balance", 0)
            vals["balance"] = self.get_balance(credit_balance, new_balance)

    @api.model
    def create(self, vals):
        self.update_balance(vals)
        return super(PosCreditUpdate, self).create(vals)

    def write(self, vals):
        self.update_balance(vals)
        return super(PosCreditUpdate, self).write(vals)

    def switch_to_confirm(self):
        self.write({"state": "confirm"})

    def switch_to_cancel(self):
        self.write({"state": "cancel"})

    def switch_to_draft(self):
        self.write({"state": "draft"})

    def do_confirm(self):
        active_ids = self._context.get("active_ids")
        for r in self.env["pos.credit.update"].browse(active_ids):
            r.switch_to_confirm()
