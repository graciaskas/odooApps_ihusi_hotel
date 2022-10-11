# -*- coding: utf-8 -*-
# License MIT (https://opensource.org/licenses/MIT).

import copy
import logging

import pytz
from pytz import timezone

from odoo import api, fields, models
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = "pos.config"

    debt_dummy_product_id = fields.Many2one(
        "product.product",
        string="Dummy Product for Debt",
        domain=[("available_in_pos", "=", True)],
        help="Dummy product used when a customer pays his debt "
        "without ordering new products. This is a workaround to the fact "
        "that Odoo needs to have at least one product on the order to "
        "validate the transaction.",
    )
    debt_type = fields.Selection(
        compute="_compute_debt_type",
        selection=[("debt", "Display Debt"), ("credit", "Display Credit")],
    )

    def _compute_debt_type(self):
        debt_type = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("pos_debt_notebook.debt_type", default="debt")
        )
        for pos in self:
            pos.debt_type = debt_type

    def init_debt_journal(self):
        user = self.env.user
        pos_payment_method_id = self.env["pos.payment.method"]
        active_debt_pos_pm = pos_payment_method_id.search(
            [
                ("cash_journal_id.company_id", "=", user.company_id.id),
                ("cash_journal_id.debt", "=", True),
            ],
            limit=1,
        )
        if active_debt_pos_pm:
            #  Check if the debt payment methods was created already for the pos company.
            return

        account_obj = self.env["account.account"]
        debt_account_old_version = account_obj.search(
            [("code", "=", "XDEBT"), ("company_id", "=", user.company_id.id)]
        )
        if debt_account_old_version:
            debt_account = debt_account_old_version[0]
        else:
            debt_account = account_obj.create(
                {
                    "name": "Debt",
                    "code": "XDEBT",
                    "user_type_id": self.env.ref(
                        "account.data_account_type_current_assets"
                    ).id,
                    "company_id": user.company_id.id,
                }
            )
            self.env["ir.model.data"].create(
                {
                    "name": "debt_account_for_company" + str(user.company_id.id),
                    "model": "account.account",
                    "module": "pos_debt_notebook",
                    "res_id": debt_account.id,
                    # If it's False, target record (res_id) will be removed while module update
                    "noupdate": True,
                }
            )

        default_debt_limit = 0
        demo_is_on = (
            self.env["ir.module.module"]
            .search([("name", "=", "pos_debt_notebook")], limit=1)
            .demo
        )
        if demo_is_on:
            self.create_demo_pos_payment_method(user, debt_account)
            default_debt_limit = 1000

        payment_methods_with_inactive_debt_journals = self.env[
            "pos.payment.method"
        ].search(
            [
                ("cash_journal_id.code", "=", "TCRED"),
                ("cash_journal_id.company_id", "=", user.company_id.id),
                ("cash_journal_id.debt", "=", False),
            ]
        )
        debt_dummy_product_id = (self.env.ref(
            "pos_debt_notebook.product_pay_debt").id,)
        common_debt_dict = {
            "debt": True,
            "credits_via_discount": False,
            "category_ids": False,
            "debt_dummy_product_id": debt_dummy_product_id,
            "debt_limit": default_debt_limit,
            "pos_cash_out": True,
        }
        if payment_methods_with_inactive_debt_journals:
            common_debt_dict.update(
                {
                    "default_debit_account_id": debt_account.id,
                    "default_credit_account_id": debt_account.id,
                }
            )
            payment_methods_with_inactive_debt_journals.mapped("cash_journal_id").write(
                common_debt_dict
            )
            pos_payment_method_id = payment_methods_with_inactive_debt_journals[0]
        else:
            common_debt_dict.update(
                {
                    "sequence_name": "Account Default Credit Journal ",
                    "prefix": "CRED ",
                    "user": user,
                    "noupdate": True,
                    "journal_name": "Credits",
                    "code": "TCRED",
                    "type": "cash",
                    "debt_account": debt_account,
                    "credits_autopay": True,
                }
            )
            pos_payment_method_id = self.create_pos_payment_method(
                common_debt_dict)
        self.write(
            {
                "payment_method_ids": [(4, pos_payment_method_id.id, False)],
                "debt_dummy_product_id": debt_dummy_product_id,
            }
        )
        current_session = self.current_session_id
        journal_id = pos_payment_method_id.cash_journal_id
        statement = [
            (
                0,
                0,
                {
                    "name": current_session.name,
                    "journal_id": journal_id.id,
                    "user_id": user.id,
                    "company_id": user.company_id.id,
                },
            )
        ]
        current_session.write({"statement_ids": statement})
        if demo_is_on:
            self.env.ref("pos_debt_notebook.product_credit_product").write(
                {"credit_product": journal_id.id}
            )

        return

    def create_pos_payment_method(self, vals):
        debt_journal = self.env["account.journal"].search(
            [("code", "=", vals["code"])], limit=1
        )
        if debt_journal:
            return debt_journal
        _logger.info("Creating '" + vals["journal_name"] + "' journal")
        user = vals["user"]
        debt_account = vals["debt_account"]
        new_sequence = self.env["ir.sequence"].create(
            {
                "name": vals["sequence_name"] + str(user.company_id.id),
                "padding": 3,
                "prefix": vals["prefix"] + str(user.company_id.id),
            }
        )
        self.env["ir.model.data"].create(
            {
                "name": "journal_sequence" + str(new_sequence.id),
                "model": "ir.sequence",
                "module": "pos_debt_notebook",
                "res_id": new_sequence.id,
                "noupdate": vals[
                    "noupdate"
                ],  # If it's False, target record (res_id) will be removed while module update
            }
        )
        debt_journal = self.env["account.journal"].create(
            {
                "name": vals["journal_name"],
                "code": vals["code"],
                "type": vals["type"],
                "debt": vals["debt"],
                "sequence_id": new_sequence.id,
                "company_id": user.company_id.id,
                "default_debit_account_id": debt_account.id,
                "default_credit_account_id": debt_account.id,
                "debt_limit": vals["debt_limit"],
                "category_ids": vals["category_ids"],
                "pos_cash_out": vals["pos_cash_out"],
                "credits_via_discount": vals["credits_via_discount"],
                "credits_autopay": vals["credits_autopay"],
            }
        )
        debt_payment_method = self.env["pos.payment.method"].create(
            {
                "name": vals["journal_name"],
                "is_cash_count": True,
                "receivable_account_id": debt_account.id,
                "cash_journal_id": debt_journal.id,
            }
        )

        self.env["ir.model.data"].create(
            {
                "name": "debt_journal_" + str(debt_journal.id),
                "model": "account.journal",
                "module": "pos_debt_notebook",
                "res_id": int(debt_journal.id),
                # If it's False, target record (res_id) will be removed while module update
                "noupdate": True,
            }
        )
        if vals.get("write_statement"):
            self.write(
                {
                    "payment_method_ids": [(4, debt_payment_method.id)],
                    "debt_dummy_product_id": vals["debt_dummy_product_id"],
                }
            )
            current_session = self.current_session_id
            statement = [
                (
                    0,
                    0,
                    {
                        "name": current_session.name,
                        "journal_id": debt_journal.id,
                        "user_id": user.id,
                        "company_id": user.company_id.id,
                    },
                )
            ]
            current_session.write({"statement_ids": statement})

        return debt_payment_method

    def open_session_cb(self):
        res = super(PosConfig, self).open_session_cb()
        current_session = self.current_session_id
        current_session.write({"state": "closed"})
        self.init_debt_journal()
        current_session.write({"state": "opened"})
        return res

    def create_demo_pos_payment_method(self, user, debt_account):
        self.create_pos_payment_method(
            {
                "sequence_name": "Account Default Credit via Discounts Journal ",
                "prefix": "CRD ",
                "user": user,
                "noupdate": True,
                "journal_name": "Credits (via discounts)",
                "code": "DCRD",
                "type": "cash",
                "debt": True,
                #  "journal_user": True,
                "debt_account": debt_account,
                "credits_via_discount": True,
                "category_ids": False,
                "write_statement": True,
                "debt_dummy_product_id": False,
                "debt_limit": 1000,
                "pos_cash_out": False,
                "credits_autopay": True,
            }
        )
        allowed_category = self.env.ref("point_of_sale.pos_category_desks").id
        self.create_pos_payment_method(
            {
                "sequence_name": "Account Default Credit Journal F&V",
                "prefix": "CRD ",
                "user": user,
                "noupdate": True,
                "journal_name": "Credits (Desks only)",
                "code": "FCRD",
                "type": "cash",
                "debt": True,
                #  "journal_user": True,
                "debt_account": debt_account,
                "credits_via_discount": False,
                "category_ids": [(6, 0, [allowed_category])],
                "write_statement": True,
                "debt_dummy_product_id": False,
                "debt_limit": 1000,
                "pos_cash_out": False,
                "credits_autopay": True,
            }
        )
