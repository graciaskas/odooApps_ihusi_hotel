# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_bulk_invoice(self, lines=True):
        active_ids = self._context.get('active_ids')
        current_user = self.env['res.users'].browse(self._context.get('uid'))

        if active_ids:
            if len(active_ids) > 1:
                account_inv_recs = self.env['account.move'].browse(active_ids)
                if account_inv_recs:
                    # Get invoice partners, types, states and payment_terms
                    partners = account_inv_recs.mapped('partner_id')
                    inv_type = account_inv_recs.mapped('type')
                    # states = account_inv_recs.mapped('state')
                    invoice_payment_term_ids = account_inv_recs.mapped(
                        'invoice_payment_term_id')

                    #customers or vendor
                    if len(partners) > 1:
                        if inv_type[0] in ('out_invoice', 'out_refund', 'out_receipt'):
                            raise UserError(
                                _("Impossible de grouper les factures car elles ne possedent pas le meme client!"))
                        else:
                            raise UserError(
                                _("Impossible de grouper les factures car elles ne possedent pas le meme fournisseur!"))
                    # Check payment_terms
                    if len(set(invoice_payment_term_ids)) > 1:
                        raise UserError(
                            _("Impossible de grouper les factures car elles ne possedent pas le meme terme de paiement!"))
                    else:
                        invoices_list = []
                        for active_id in active_ids:
                            invoice = self.env['account.move'].browse(
                                active_id)
                            if invoice:
                                lines = []
                                for line in invoice.invoice_line_ids:
                                    lines.append({
                                        'currency': line.currency_id.name,
                                        'product': line.product_id.name,
                                        'name': line.name,

                                        # 'tax_ids': [(6, 0, line.tax_ids.ids)],
                                        'quantity': line.quantity,
                                        'product_uom': line.product_uom_id.name,
                                        'price_unit': line.price_unit,
                                        'total': line.price_unit * line.quantity
                                        # 'date_planned': line.date_planned,
                                    })
                                #  Invoices with lines,
                                invoices_list.append({
                                    'name': invoice.name,
                                    'amount_total': invoice.amount_total,
                                    'invoice_date': invoice.invoice_date,
                                    'partner_id': invoice.partner_id.name,
                                    'amount_tax': invoice.amount_tax,
                                    'currency': invoice.currency_id.name,
                                    'lines': lines
                                })
                        docargs = {
                            'ids': self.ids,
                            'model': self._name,
                            'date':  datetime.now().strftime("%d/%m/%Y  %H:%M:%S"),
                            'partner': partners.parent_id.name or '',
                            'contact': partners.name or '',
                            'current_user': current_user and current_user.name,
                            'records': invoices_list
                        }
                        # raise UserError(_(inv_type))
                        if lines == True:
                            return self.env.ref('grc_bulk_invoice.bulk_invoice_report').report_action(self, docargs)
                    return self.env.ref('grc_bulk_invoice.bulk_invoice_report2').report_action(self, docargs)

            else:
                raise UserError(_("Veillez selectionner plus d'une facture!"))
