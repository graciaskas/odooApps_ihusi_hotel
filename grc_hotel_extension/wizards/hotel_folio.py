# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class FolioReportWizardInherit(models.TransientModel):
    _inherit = "folio.report.wizard"

    def print_folios(self):
        data = {
            "ids": self.ids,
            "model": "hotel.folio",
            "form": self.read(["date_start", "date_end"])[0],
        }
        return self.env.ref("grc_hotel_extension.report_folios").report_action(
            self, data=data
        )
