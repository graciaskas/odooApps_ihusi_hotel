# _*_ coding : utf-8 _*_
import logging

from email.policy import default
from odoo import models, api, fields, _
from odoo.exceptions import except_orm, ValidationError

_logger = logging.getLogger(__name__)


class HotelFolio(models.Model):
    _name = 'hotel.folio'
    _inherit = ['portal.mixin', 'hotel.folio',
                'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = "checkin_date desc"

    product_id = fields.Char("Room", ondelete="restrict")
    duration = fields.Float(
        string="Days",
        help="Number of days which will automatically "
        "count from the check-in and check-out date. ",
    )

    note_folio = fields.Text("Note", tracking=2)
    room_line_ids = fields.One2many(
        "hotel.folio.line",
        "folio_id",
        readonly=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
        help="Hotel room reservation detail.",
        tracking=1
    )

    def action_view_order(self):
        return {
            'name': _('Customer Invoice'),
            'view_mode': 'form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'res_id': self.order_id.id,
        }

    def action_confirm(self):
        for order in self.order_id:
            order.state = "sale"
            if not order.analytic_account_id:
                for line in order.order_line:
                    if line.product_id.invoice_policy == "cost":
                        order._create_analytic_account()
                        break
        config_parameter_obj = self.env["ir.config_parameter"]
        if config_parameter_obj.sudo().get_param("sale.auto_done_setting"):
            self.order_id.action_done()

        """
        When a check out is processed.The system will automaticaly remove the room reservation line
        and set the room state as avaible.
        Author: <graciaskas96@gmail.com>
        """
        self.env["hotel.room.reservation.line"].search(
            [("reservation_id", "=", self.reservation_id.id)]
        ).unlink()
        # Update room status
        for line in self.room_line_ids:
            self.env["hotel.room"].search([("name", "=", line.product_id.name)]).update(
                {
                    "status": "available",
                    "isroom": True,
                }
            )

    def action_cancel_draft(self):
        """
        @param self: object pointer
        """
        if not len(self._ids):
            return False
        query = "select id from sale_order_line \
        where order_id IN %s and state=%s"
        self._cr.execute(query, (tuple(self._ids), "cancel"))
        cr1 = self._cr
        line_ids = map(lambda x: x[0], cr1.fetchall())
        self.write({"state": "draft", "invoice_ids": []})
        sale_line_obj = self.env["sale.order.line"].browse(line_ids)
        sale_line_obj.write(
            {
                "invoice_status": "no",
                "state": "draft",
                "invoice_lines": [(6, 0, [])],
            }
        )
        return True

    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @raise: Validation error.
        """
        raise ValidationError("You cannot delete a folio once created !")
