# See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class FolioReportInherit(models.AbstractModel):
    _name = "report.grc_hotel_extension.report_folio"

    # function to return total days according to date difference
    def get_days(self, date_start, date_end):
        start = datetime.strptime(str(date_start), "%Y-%m-%d  %H:%M:%S")
        end = datetime.strptime(str(date_end), "%Y-%m-%d  %H:%M:%S")
        delta = end - start
        days = delta.days
        hours = delta.seconds / 3600
        if hours > 20:
            days += 1
        if days == 0:
            days = 1
        return days

    def _get_folio_data(self, date_start, date_end):
        total_amount = 0.0
        data_folio = []
        folio_obj = self.env["hotel.folio"].search([("state", "=", 'draft')])
        tids = folio_obj
        for data in tids:
            reservation = self.env['hotel.reservation'].search(
                [('id', '=', data.reservation_id.id)]
            )
            reserve = reservation['reservation_line_ids'][0].reserve[0]
            quantity = self.get_days(
                data['checkin_date'], data['checkout_date'])
            total = quantity * reservation.room_price
            data_folio.append(
                {
                    "reservation_no": reservation.reservation_no,
                    "name": data.name,
                    'product_id': reserve.name,
                    'price_unit': reserve.list_price,
                    'room_price': reservation.room_price,
                    'discount': reserve.list_price - reservation.room_price,
                    'quantity': quantity,
                    "partner": data.partner_id.name,
                    "company": data.partner_id.parent_id.name or "",
                    "checkin": data.checkin_date,
                    "checkout": data.checkout_date,
                    'total': total
                }
            )
            total_amount += total
        data_folio.append({"total_amount": total_amount})
        return data_folio

    @api.model
    def _get_report_values(self, docids, data):
        self.model = self.env.context.get("active_model")
        if data is None:
            data = {}
        if not docids:
            docids = data["form"].get("docids")
        folio_profile = self.env["hotel.folio"].browse(docids)
        date_start = data["form"].get("date_start", fields.Date.today())
        date_end = data["form"].get(
            "date_end",
            str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[
                :10
            ],
        )
        return {
            "doc_ids": docids,
            "doc_model": self.model,
            "data": data["form"],
            "docs": self.env["hotel.folio"].search([('state', '=', 'draft')]),
            "time": time,
            'now': fields.Date.today(),
            "folio_data": self._get_folio_data(date_start, date_end),
        }
