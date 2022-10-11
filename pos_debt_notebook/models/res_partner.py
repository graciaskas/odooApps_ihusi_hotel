# -*- coding: utf-8 -*-
# License MIT (https://opensource.org/licenses/MIT).

import copy
import logging

import pytz
from pytz import timezone

from odoo import api, fields, models
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends("report_pos_debt_ids")
    def _compute_debt(self):
        domain = [("partner_id", "in", self.ids)]
        fields = ["partner_id", "balance"]
        res = self.env["report.pos.debt"].read_group(
            domain, fields, "partner_id")
        res_index = {id: {"balance": 0} for id in self.ids}
        for data in res:
            res_index[data["partner_id"][0]] = data
        for r in self:
            r.debt = -res_index[r.id]["balance"]
            r.credit_balance = -r.debt

    @api.depends("report_pos_debt_ids")
    def _compute_debt_company(self):
        partners = self.filtered(lambda r: len(r.child_ids))
        for r in self - partners:
            r.debt_company = None
            r.credit_balance_company = None

        if not partners:
            for record in self:
                record.debt_company = 0.0
                record.credit_balance_company = 0.0
            return

        domain = [("partner_id", "in", partners.ids +
                   partners.mapped("child_ids").ids)]
        fields = ["partner_id", "balance"]
        res = self.env["report.pos.debt"].read_group(
            domain, fields, "partner_id")

        res_index = {id: 0 for id in partners.ids}
        for data in res:
            pid = data["partner_id"][0]
            balance = data["balance"]
            for r in partners:
                if pid == r.id or pid in r.child_ids.ids:
                    res_index[r.id] += balance

        for r in partners:
            r.debt_company = -res_index[r.id]
            r.credit_balance_company = -r.debt_company

    def debt_history(self, limit=0):
        """
        Get debt details

        :param int limit: max number of records to return
        :return: dictionary with keys:
             * partner_id: partner identification
             * debt: current debt
             * debts: dictionary with keys:

                 * balance
                 * journal_id: list

                    * id
                    * name
                    * code

             * records_count: total count of records
             * history: list of dictionaries

                 * date
                 * config_id
                 * balance
                 * journal_code

        """
        fields = [
            "date",
            "config_id",
            "order_id",
            "move_id",
            "balance",
            "product_list",
            "journal_id",
            "partner_id",
        ]
        debt_journals = self.env["account.journal"].search(
            [("debt", "=", True)])
        data = {
            id: {
                "history": [],
                "partner_id": id,
                "debt": 0,
                "records_count": 0,
                "debts": {
                    dj.id: {
                        "balance": 0,
                        "journal_id": [dj.id, dj.name],
                        "journal_code": dj.code,
                    }
                    for dj in debt_journals
                },
            }
            for id in self.ids
        }

        records = self.env["report.pos.debt"].read_group(
            domain=[
                ("partner_id", "in", self.ids),
                ("journal_id", "in", debt_journals.ids),
            ],
            fields=fields,
            groupby=["partner_id", "journal_id"],
            lazy=False,
        )
        for rec in records:
            partner_id = rec["partner_id"][0]
            data[partner_id]["debts"][rec["journal_id"]
                                      [0]]["balance"] = rec["balance"]
            data[partner_id]["records_count"] += rec["__count"]
            # -= due to it's debt, and balances per journals are credits
            data[partner_id]["debt"] -= rec["balance"]

        if limit:
            for partner_id in self.ids:
                data[partner_id]["history"] = self.env["report.pos.debt"].search_read(
                    domain=[("partner_id", "=", partner_id)],
                    fields=fields,
                    limit=limit,
                )
                for rec in data[partner_id]["history"]:
                    rec["date"] = self._get_date_formats(rec["date"])
                    rec["journal_code"] = data[partner_id]["debts"][
                        rec["journal_id"][0]
                    ]["journal_code"]

        return data

    debt = fields.Float(
        compute="_compute_debt",
        string="Debt",
        readonly=True,
        digits="Account",
        help="Debt of this partner only.",
    )
    credit_balance = fields.Float(
        compute="_compute_debt",
        string="Credit",
        readonly=True,
        digits="Account",
        help="Credit balance of this partner only.",
    )
    debt_company = fields.Float(
        compute="_compute_debt_company",
        string="Total Debt",
        readonly=True,
        digits="Account",
        help="Debt value of this company (including its contacts)",
    )
    credit_balance_company = fields.Float(
        compute="_compute_debt_company",
        string="Total Credit",
        readonly=True,
        digits="Account",
        help="Credit balance of this company (including its contacts)",
    )
    debt_type = fields.Selection(
        compute="_compute_debt_type",
        selection=[("debt", "Display Debt"), ("credit", "Display Credit")],
    )
    report_pos_debt_ids = fields.One2many(
        "pos.credit.update",
        "partner_id",
        help="Technical field for proper recomputations of computed fields",
    )

    def _get_date_formats(self, date):

        lang_code = self.env.user.lang or "en_US"
        lang = self.env["res.lang"]._lang_get(lang_code)
        date_format = lang.date_format
        time_format = lang.time_format
        fmt = date_format + " " + time_format
        utc_tz = pytz.utc.localize(date, is_dst=False)
        user_tz = self.env.user.tz
        user_tz = user_tz and timezone(self.env.user.tz) or timezone("GMT")
        final = utc_tz.astimezone(user_tz)

        return final.strftime(fmt)

    def _compute_debt_type(self):
        debt_type = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("pos_debt_notebook.debt_type", default="debt")
        )
        for partner in self:
            partner.debt_type = debt_type

    @api.model
    def create_from_ui(self, partner):
        if partner.get("debt_limit") is False:
            del partner["debt_limit"]
        return super(ResPartner, self).create_from_ui(partner)

    def _compute_partner_journal_debt(self, journal_id):
        domain = [("partner_id", "in", self.ids),
                  ("journal_id", "=", journal_id)]
        fields = ["partner_id", "balance", "journal_id"]
        res = self.env["report.pos.debt"].read_group(
            domain, fields, "partner_id")

        res_index = {id: {"balance": 0} for id in self.ids}

        for data in res:
            res_index[data["partner_id"][0]] = data
        return res_index
