# _*_ coding : utf-8 _*_
import time
from datetime import datetime, timedelta

from odoo import _, api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


def _offset_format_timestamp1(
    src_tstamp_str,
    src_format,
    dst_format,
    ignore_unparsable_time=True,
    context=None,
):
    if not src_tstamp_str:
        return False
    res = src_tstamp_str
    if src_format and dst_format:
        try:
            # dt_value needs to be a datetime object\
            # (so notime.struct_time or mx.DateTime.DateTime here!)
            dt_value = datetime.strptime(src_tstamp_str, src_format)
            if context.get("tz", False):
                try:
                    import pytz

                    src_tz = pytz.timezone(context["tz"])
                    dst_tz = pytz.timezone("UTC")
                    src_dt = src_tz.localize(dt_value, is_dst=True)
                    dt_value = src_dt.astimezone(dst_tz)
                except Exception:
                    pass
            res = dt_value.strftime(dst_format)
        except Exception:
            # Normal ways to end up here are if strptime or strftime failed
            if not ignore_unparsable_time:
                return False
            pass
    return res


class HotelFolioLine(models.Model):
    _name = 'hotel.folio.line'
    _inherit = ['portal.mixin', 'hotel.folio.line',
                'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    def _get_checkin_date(self):
        if "checkin" in self._context:
            return self._context["checkin"]
        return time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    @api.model
    def _get_checkout_date(self):
        if "checkout" in self._context:
            return self._context["checkout"]
        return time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    checkin_date = fields.Datetime(
        "Check In", required=True, default=_get_checkin_date, track_visibility='always')
    checkout_date = fields.Datetime(
        "Check Out", required=True, default=_get_checkout_date, track_visibility='always')

    @api.constrains("checkin_date", "checkout_date")
    def check_dates(self):
        """
        This method is used to validate the checkin_date and checkout_date.
        -------------------------------------------------------------------
        @param self: object pointer
        @return: raise warning depending on the validation
        """
        if self.checkin_date >= self.checkout_date:
            raise ValidationError(
                _(
                    """Room line Check In Date Should be """
                    """less than the Check Out Date!"""
                )
            )

    # @api.model
    # def _get_checkin_date(self):
    #     if self._context.get("tz"):
    #         to_zone = self._context.get("tz")
    #     else:
    #         to_zone = "UTC"
    #     return _offset_format_timestamp1(
    #         time.strftime("%Y-%m-%d 12:00:00"),
    #         DEFAULT_SERVER_DATETIME_FORMAT,
    #         DEFAULT_SERVER_DATETIME_FORMAT,
    #         ignore_unparsable_time=True,
    #         context={"tz": to_zone},
    #     )

    # Change folio duration and checkout date base on room line
    # Only one room line is allowed
    @api.onchange('checkout_date')
    def _onchange_checkout_date(self):
        folio_id = self.env['hotel.folio'].search(
            [('id', '=', self.folio_id._origin.id)])
        if folio_id:
            folio_id.update({
                'checkout_date': self.checkout_date,
                # 'duration': self.product_uom_qty,
                # 'duration_dummy': self.product_uom_qty
            })
        else:
            raise UserError(
                _('Impossible de trouver le folio pour cette ligne'))

    # Make it readOnly
    checkin_date = fields.Datetime(
        string="Check In",
        required=True,
        default=_get_checkin_date,
        tracking=True
        # readonly=True
    )
