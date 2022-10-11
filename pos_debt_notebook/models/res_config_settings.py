# -*- coding: utf-8 -*-
# License MIT (https://opensource.org/licenses/MIT).

import copy
import logging

import pytz
from pytz import timezone

from odoo import api, fields, models
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    debt_type = fields.Selection(
        [("debt", "Display Debt"), ("credit", "Display Credit")],
        default="debt",
        string="Debt Type",
        help="Way to display debt value (label and sign of the amount). "
        "In both cases debt will be red, credit - green",
    )

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        for record in self:
            config_parameters.set_param(
                "pos_debt_notebook.debt_type", record.debt_type)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        res.update(
            debt_type=config_parameters.get_param(
                "pos_debt_notebook.debt_type", default="debt"
            ),
        )
        return res
