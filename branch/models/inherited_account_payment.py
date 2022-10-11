# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)

        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            rec['communication'] = invoice['name'] or invoice['number']
            rec['currency_id'] = invoice['currency_id'][0]
            rec['payment_type'] = invoice['type'] in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
            rec['partner_type'] = MAP_INVOICE_TYPE_PARTNER_TYPE[invoice['type']]
            rec['partner_id'] = invoice['partner_id'][0]
            rec['amount'] = invoice['amount_residual']
            rec['branch_id'] = invoice.get('branch_id') and invoice.get('branch_id')[0]
        return rec

    branch_id = fields.Many2one('res.branch')


    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        selected_brach = self.branch_id
        if selected_brach:
            user_id = self.env['res.users'].browse(self.env.uid)
            user_branch = user_id.sudo().branch_id
            if user_branch and user_branch.id != selected_brach.id:
                raise UserError("Please select active branch only. Other may create the Multi branch issue. \n\ne.g: If you wish to add other branch then Switch branch from the header and set that.") 

