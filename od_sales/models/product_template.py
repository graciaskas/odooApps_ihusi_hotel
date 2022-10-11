# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    computer_generation = fields.Char(string='Computer generation')
    waranty_start = fields.Date(string='Waranty start date')
    waranty_end = fields.Date(string='Waranty end date')
