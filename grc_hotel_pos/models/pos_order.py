# _*_ coding: utf-8 _*_
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from email.policy import default
import pytz
from odoo import api, fields, models, tools, _


class PosOrder(models.Model):
    _inherit = "pos.order"

    folio_room = fields.Char("Room", default='Facture ordinaire')

    def _prepare_invoice_vals(self):
        self.ensure_one()

        timezone = pytz.timezone(self._context.get(
            'tz') or self.env.user.tz or 'UTC')

        folio = self.env["hotel.folio"].search(
            [("state", "=", "draft"), ("partner_id", "=", self.partner_id.id)]
        )

        vals = {
            'invoice_payment_ref': self.name,
            'journal_id': self.session_id.config_id.invoice_journal_id.id,
            'type': 'out_invoice' if self.amount_total >= 0 else 'out_refund',
            'ref': self.name,
            'partner_id': self.partner_id.id,
            'narration': self.note or '',
            'invoice_origin': self.name,
            # considering partner's sale pricelist's currency
            'currency_id': self.pricelist_id.currency_id.id,
            'invoice_user_id': self.user_id.id,
            'invoice_date': self.date_order.astimezone(timezone).date(),
            'fiscal_position_id': self.fiscal_position_id.id,
            'invoice_line_ids': [(0, None, self._prepare_invoice_line(line)) for line in self.lines],
        }

        if folio:
            self.update({'folio_room': folio.product_id})
            vals.update({
                'invoice_origin': folio.order_id.name
            })
            # Get default product to use
            product = self.env["product.template"].search([("id", "=", 141)])
            # total order restaurant and bar
            service_bar = 0.0
            service_restaurant = 0.0
            service_buanderie = 0.0
            # pos order line
            line_obj = self.env["pos.order.line"].search(
                [("order_id", "=", self.id)])

            for line in line_obj:
                type_name = self.env['product.category'].search(
                    [('id', '=', line['product_id'].categ_id.id)]).name
                categ_name = self.env['product.category'].search(
                    [('id', '=', line['product_id'].categ_id.id)]).name
                # if type == restaurant
                if categ_name == 'Restaurant' or categ_name.find('Restaurant') > 0:
                    service_restaurant += line.price_unit * line.qty
                elif categ_name == "Bar" or categ_name.find("Bar") > 0:
                    service_bar += line.price_unit * line.qty
                elif categ_name == "Buanderie" or categ_name.find("Bar") > 0:
                    service_buanderie += line.price_unit * line.qty
                else:
                    pass

            vals_sale = {
                "customer_lead": 0,
                "product_id": product.id,
                "product_uom": product.uom_id.id,
                "product_uom_qty": 1,
                "product_updatable": product.id,
                "price_total": 0,
                "name": "[Services bar"+" "+str(self.date_order)+"]",
                "order_id": folio.order_id.id,
                "order_partner_id": self.partner_id.id,
                "state": "draft",
                "invoice_status": "invoiced",
                "discount": 0,
                "price_unit": 0,
                "salesman_id": self.user_id.id,
            }

            if service_bar > 0:
                vals_sale.update({
                    'price_unit': service_bar,
                    'price_total': service_bar,
                    "name": "[Services bar"+" "+str(self.date_order)+"]",
                })
                self.env["sale.order.line"].sudo().create(vals_sale)
            if service_restaurant > 0:
                vals_sale.update({
                    'price_unit': service_restaurant,
                    'price_total': service_restaurant,
                    "name": "[Services restaurant"+" "+str(self.date_order)+"]",
                })
                self.env["sale.order.line"].sudo().create(vals_sale)
            if service_buanderie > 0:
                vals_sale.update({
                    'price_unit': service_buanderie,
                    'price_total': service_buanderie,
                    "name": "[Services buanderie"+" "+str(self.date_order)+"]",
                })
                self.env["sale.order.line"].sudo().create(vals_sale)
        return vals
