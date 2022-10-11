# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class QuickRoomReservation(models.TransientModel):
    _inherit = "quick.room.reservation"

    room_price = fields.Float(
        string='Room price',
        required=True,
        default='1.0',
        help='The price 0f the room'
    )

    commission_agent = fields.Many2one(
        'res.partner',
        string='Commission for the agent',
        help='Commission for the agent'
    )

    reservation_type = fields.Selection(
        [('room', 'Room'), ('floor', 'Floor'), ('space', 'Space')],
        string='Reservation type',
        required=True,
        help='The type 0f the reservation'
    )

    def room_reserve(self):
        """
        This method create a new record for hotel.reservation
        -----------------------------------------------------
        @param self: The object pointer
        @return: new record set for hotel reservation.
        """
        hotel_res_obj = self.env["hotel.reservation"]
        for res in self:
            rec = hotel_res_obj.create(
                {
                    "partner_id": res.partner_id.id,
                    "partner_invoice_id": res.partner_invoice_id.id,
                    "partner_order_id": res.partner_order_id.id,
                    "partner_shipping_id": res.partner_shipping_id.id,
                    "checkin": res.check_in,
                    "checkout": res.check_out,
                    "warehouse_id": res.warehouse_id.id,
                    "pricelist_id": res.pricelist_id.id,
                    "adults": res.adults,
                    "reservation_type": self.reservation_type,
                    "room_price": self.room_price,
                    "reservation_line_ids": [
                        (
                            0,
                            0,
                            {
                                "reserve": [(6, 0, [res.room_id.id])],
                                "name": (
                                    res.room_id and res.room_id.name or ""
                                ),
                            },
                        )
                    ],
                }
            )
        return rec
