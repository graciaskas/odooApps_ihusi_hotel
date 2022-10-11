from email.policy import default
from odoo import models, api, fields


class HotelReservation(models.Model):
    _inherit = 'hotel.reservation'

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

    receptionist = fields.Many2one(
        'res.users',
        string='Receptionist',
        help='Receptionist',
        default=lambda self: self.env.user
    )

    reservation_type = fields.Selection(
        [('room', 'Room'), ('floor', 'Floor'), ('space', 'Space')],
        string='Reservation type',
        required=True,
        help='The type 0f the reservation'
    )

    def create_folio(self):
        """
        This method is for create new hotel folio.
        -----------------------------------------
        @param self: The object pointer
        @return: new record set for hotel folio.
        """
        for reservation in self:
            folio_lines = []
            checkin_date = reservation["checkin"]
            checkout_date = reservation["checkout"]
            duration_vals = self._onchange_check_dates(
                checkin_date=checkin_date,
                checkout_date=checkout_date,
                duration=False,
            )
            duration = duration_vals.get("duration") or 0.0
            folio_vals = {
                "date_order": reservation.date_order,
                "warehouse_id": reservation.warehouse_id.id,
                "partner_id": reservation.partner_id.id,
                "pricelist_id": reservation.pricelist_id.id,
                "partner_invoice_id": reservation.partner_invoice_id.id,
                "partner_shipping_id": reservation.partner_shipping_id.id,
                "checkin_date": reservation.checkin,
                "checkout_date": reservation.checkout,
                "duration": duration,
                "reservation_id": reservation.id,
            }

            for line in reservation.reservation_line_ids:
                for r in line.reserve:
                    folio_lines.append(
                        (
                            0,
                            0,
                            {
                                "checkin_date": checkin_date,
                                "checkout_date": checkout_date,
                                "product_id": r.product_id and r.product_id.id,
                                "name": r.product_id and r.product_id.name,
                                # update price to reservation price
                                "price_unit": reservation.room_price,
                                "price_reduce": reservation.room_price,
                                "product_uom_qty": duration,
                                "is_reserved": True,
                            },
                        )
                    )
                    r.write({"status": "occupied", "isroom": False})
            folio_vals.update({"room_line_ids": folio_lines})

            # Try to bind first product to folio
            for rec in self:
                if len(rec.reservation_line_ids) == 1:
                    for line in rec.reservation_line_ids:
                        for room in line.reserve:
                            room = self.env["hotel.room"].search(
                                [("product_id", "=", room.product_id.id)])
                            folio_vals.update({"product_id":  room.name})
            # Create new folio
            folio = self.env["hotel.folio"].create(folio_vals)

            self.write({"folios_ids": [(6, 0, folio.ids)], "state": "done"})
        return True
