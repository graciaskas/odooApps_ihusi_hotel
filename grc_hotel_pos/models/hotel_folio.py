# _*_ coding: utf-8 _*_
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from email.policy import default
import pytz
from odoo import api, fields, models, tools, _


class PosOrder(models.Model):
    _inherit = "hotel.folio"

    # def _get_ordername(self):
    #     return self.order_id.name

    # invoices = fields.Many2many(
    #     'account.move',
    #     'partner_id',
    #     string='Invoices',
    #     readonly=True
    # )
    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        """
        @param self: object pointer
        """
        room_lst = []
        invoice_id = self.order_id.action_invoice_create(
            grouped=False, final=False)
        for line in self:
            values = {"invoiced": True, "hotel_invoice_id": invoice_id}
            line.write(values)
            for rec in line.room_lines:
                room_lst.append(rec.product_id)
            for room in room_lst:
                room_obj = self.env["hotel.room"].search(
                    [("name", "=", room.name)])
                room_obj.write({"isroom": True})
        return invoice_id
