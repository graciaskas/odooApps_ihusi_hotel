# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from unicodedata import name
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class BulkInvoice(models.Model):
    _name = 'bulk.invoice'
    _order = "name"

    name = fields.Char('invoice name')

    @api.model
    def create(self, vals):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        vals["name"] = (
            self.env["ir.sequence"].next_by_code("bulk.invoice") or "New"
        )
        return super(BulkInvoice, self).create(vals)
