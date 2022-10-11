from odoo import fields, models, api, _
import base64


class PosOrder(models.Model):
    _inherit = 'pos.order'

    quotation_id = fields.Many2one('pos.quotation')
    quotation_name = fields.Char("Quotation Name")
    seller_id = fields.Many2one("res.users", string="Seller")

    @api.model
    def _order_fields(self, ui_order):
        data = super(PosOrder, self)._order_fields(ui_order)
        data.update({
            'quotation_id': ui_order.get('quotation_id') or False,
            'quotation_name': ui_order.get('quotation_name') or False,
            'seller_id': ui_order.get('seller_id') or False,
        })
        return data

    @api.model
    def create(self, vals):
        orders = super(PosOrder, self).create(vals)
        if orders.quotation_id:
            orders.quotation_id.write({'state': 'loaded'})
        return orders

    def action_receipt_to_customer(self, name, client, ticket):
        if not self:
            return False
        if not client.get('email'):
            return False

        message = _("<p>Dear %s,<br/>Here is your electronic ticket for the %s. </p>") % (client['name'], name)
        filename = 'Receipt-' + name + '.jpg'
        vals = {
            'name': filename,
            'type': 'binary',
            'datas': ticket,
            'res_model': 'pos.order',
            'store_fname': filename,
            'mimetype': 'image/jpeg',
        }
        if self.ids:
            vals['res_id'] = self.ids[0]
        receipt = self.env['ir.attachment'].create(vals)
        mail_values = {
            'subject': _('Receipt %s', name),
            'body_html': message,
            'author_id': self.env.user.partner_id.id,
            'email_from': self.env.company.email or self.env.user.email_formatted,
            'email_to': client['email'],
            'attachment_ids': [(4, receipt.id)],
        }

        if self.mapped('account_move') and self.ids:
            report = self.env.ref('point_of_sale.pos_invoice_report')._render_qweb_pdf(self.ids[0])
            filename = name + '.pdf'
            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'type': 'binary',
                'datas': base64.b64encode(report[0]),
                'store_fname': filename,
                'res_model': 'pos.order',
                'res_id': self.ids[0],
                'mimetype': 'application/x-pdf'
            })
            mail_values['attachment_ids'] += [(4, attachment.id)]

        mail = self.env['mail.mail'].sudo().create(mail_values)
        mail.send()
