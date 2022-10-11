# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError

class ResUsers(models.Model):
    _inherit = 'res.users'

    branch_ids = fields.Many2many('res.branch',string="Allowed Branch")
    branch_id = fields.Many2one('res.branch', string= 'Branch')

    def write(self, values):
        if 'branch_id' in values or 'branch_ids' in values:
            self.env['ir.model.access'].call_cache_clearing_methods()
            self.env['ir.rule'].clear_caches()
        user = super(ResUsers, self).write(values)
        return user

    @api.constrains('branch_id', 'branch_ids')
    def _check_branch(self):
        for user in self:
            if (user.branch_id.id or user.branch_ids.ids != []) and user.branch_id not in user.branch_ids:
                raise ValidationError(_('The chosen branch is not in the allowed branch for this user'))