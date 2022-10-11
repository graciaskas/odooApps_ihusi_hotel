# See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ReportConfirmReservation(models.AbstractModel):
    _name = "report.grc_hotel_extension.report_confirm_reservations"
    _description = "Auxiliar to get the check in report"

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

    def _get_confirm_room_reservation(self):
        reservations = self.env["hotel.reservation"].search(
            [("state", "=", 'confirm'), ("reservation_type", "=", 'room')]
        )
        docs = []
        for reservation in reservations:
            reserve = reservation['reservation_line_ids'][0].reserve[0]
            quantity = self.get_days(
                reservation['checkin'], reservation['checkout'])
            docs.append({
                'reservation_no': reservation['reservation_no'],
                'partner_id': reservation['partner_id'].name,
                'checkin': reservation['checkin'],
                'checkout': reservation['checkout'],
                'product_id': reserve.name,
                'room_price': reservation['room_price'],
                'categ_id': reserve.categ_id,
                'list_price': reserve.list_price,
                'discount': reserve.list_price - reservation['room_price'],
                'quantity': quantity,
                'total': quantity * reservation['room_price']
            })

        return docs

    def _get_confirm_other_reservation(self):
        reservations = self.env["hotel.reservation"].search(
            [("state", "=", 'confirm'), ("reservation_type", "!=", 'room')]
        )
        docs = []
        for reservation in reservations:
            reserve = reservation['reservation_line_ids'][0].reserve[0]
            quantity = self.get_days(
                reservation['checkin'], reservation['checkout'])
            docs.append({
                'reservation_no': reservation['reservation_no'],
                'partner_id': reservation['partner_id'].name,
                'checkin': reservation['checkin'],
                'checkout': reservation['checkout'],
                'product_id': reserve.name,
                'room_price': reservation['room_price'],
                'categ_id': reserve.categ_id,
                'list_price': reserve.list_price,
                'discount': reserve.list_price - reservation['room_price'],
                'quantity': quantity,
                'total': quantity * reservation['room_price']
            })

        return docs

    @api.model
    def _get_report_values(self, docids, data):
        active_model = self.env.context.get("active_model")

        return {
            "doc_ids": docids,
            "doc_model": active_model,
            "data": data["form"],
            "get_rooms": self._get_confirm_room_reservation(),
            "get_others": self._get_confirm_other_reservation(),
            "time": time,
            'now': fields.Date.today(),
        }
