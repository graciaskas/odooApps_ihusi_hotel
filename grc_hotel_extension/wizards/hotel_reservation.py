# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ReservationReportWizardInherit(models.TransientModel):
    _inherit = "hotel.reservation.wizard"

    def report_confirm_reservation(self):
        data = {
            "ids": self.ids,
            "model": "hotel.folio",
            "form": self.read(["date_start", "date_end"])[0],
        }
        return self.env.ref("grc_hotel_extension.report_confirm_reservation").report_action(
            self, data=data
        )

    def report_checkin_reservation(self):
        data = {
            "ids": self.ids,
            "model": "hotel.folio",
            "form": self.read(["date_start", "date_end"])[0],
        }
        return self.env.ref("grc_hotel_extension.report_checkin_reservation").report_action(
            self, data=data
        )
