# -*- coding: utf-8 -*-
# License MIT (https://opensource.org/licenses/MIT).

import copy
import logging

import pytz
from pytz import timezone

from odoo import api, fields, models
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)


class Product(models.Model):

    _inherit = "product.template"

    credit_product = fields.Many2one(
        "account.journal",
        string="Journal Credit Product",
        domain="[('debt', '=', True)]",
        help="This product is used to buy Credits (pay for debts).",
    )
