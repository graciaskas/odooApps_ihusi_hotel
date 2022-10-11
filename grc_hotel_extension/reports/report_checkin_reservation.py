# See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ReportCheckinReservation(models.AbstractModel):
    _name = "report.grc_hotel_extension.report_checkin_reservations"
    _description = "Auxiliar to get the check in report"

    def _get_checkin_reservation(self, date_start, date_end):
        reservations = self.env["hotel.reservation"].search(
            [
                ("checkin", ">=", date_start),
                ("checkout", "<=", date_end),
                ("state", "=", 'done')
            ]
        )
        return reservations

    @api.model
    def _get_report_values(self, docids, data):
        active_model = self.env.context.get("active_model")
        if data is None:
            data = {}
        if not docids:
            docids = data["form"].get("docids")
        folio_profile = self.env["hotel.reservation"].browse(docids)
        date_start = data.get("date_start", fields.Date.today())
        date_end = data["form"].get(
            "date_end",
            str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[
                :10
            ],
        )
        rm_act = self.with_context(data["form"].get("used_context", {}))
        _get_checkin_reservation = rm_act._get_checkin_reservation(
            date_start, date_end
        )
        return {
            "doc_ids": docids,
            "doc_model": active_model,
            "data": data["form"],
            "docs": folio_profile,
            "time": time,
            "get_checkin": _get_checkin_reservation,
        }
