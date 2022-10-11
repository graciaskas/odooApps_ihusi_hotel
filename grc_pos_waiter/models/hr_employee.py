# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    is_waiter = fields.Boolean(string="Is Waiter ?", default=False,
                               help='Enable to mark the  employee as a waiter')

    def unlink(self):
        raise UserError(
            _('You cannot delete a waiter'))

    @api.model
    def create(self, vals):
        if not vals:
            vals = {}
        if self._context is None:
            self._context = {}
        vals["is_waiter"] = True
        return super(HrEmployee, self).create(vals)
