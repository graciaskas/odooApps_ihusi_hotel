# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import hashlib
import json
from odoo import api, models
from odoo.http import request
from odoo.tools import ustr
from odoo.addons.web.controllers.main import module_boot, HomeStaticTemplateHelpers
import odoo

class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        user = request.env.user
        result = super(Http, self).session_info()
        result.update({
            'branch_id' : user.branch_id.id if request.session.uid else None,
        })
        if self.env.user.has_group('base.group_user'):
            result.update({
                "user_branches": {'current_branch': (user.branch_id.id, user.branch_id.name), 'allowed_branch': [(comp.id, comp.name) for comp in user.branch_ids]},
                "display_switch_branch_menu": user.has_group('branch.group_multi_branch') and len(user.branch_ids) > 1,
                "allowed_branch_ids" : user.branch_id.ids
            })
        return result
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: