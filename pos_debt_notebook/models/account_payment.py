# -*- coding: utf-8 -*-
# License MIT (https://opensource.org/licenses/MIT).

import copy
import logging

import pytz
from pytz import timezone

from odoo import api, fields, models
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    has_invoices = fields.Boolean(store=True, compute_sudo=False)
    company_id = fields.Many2one(store=True, compute_sudo=False)
