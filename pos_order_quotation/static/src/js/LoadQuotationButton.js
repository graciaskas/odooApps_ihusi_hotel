odoo.define("pos_order_quotation.LoadQuotationButton", function(require) {
    "use strict";

    var pos_model = require('point_of_sale.models');
    var screens = require("point_of_sale.screens");


    //create a new button by extending the base ActionButonWidget
    var LoadQuotationButton = screens.ActionButtonWidget.extend({
        template: 'LoadQuotationButton',
        
        getCurrentOrder() {
            return this.env.pos.get_order();
        },

        button_click: async function () {
            var self = this;

            const {
                confirmed,
                payload: selectedQuotation
            } = await this.showPopup(
                'LoadQuotationPopup', {
                    title: this.env._t('Select Quotation'),
                    confirmText: this.env._t('Load'),
                    cancelText: this.env._t('Cancel'),
                }
            );

            if (confirmed) {
                var error = false;
                var self = this;
                self.rpc({
                    model: 'pos.quotation',
                    method: 'get_quotation_details',
                    args: [selectedQuotation.id],
                }).catch(function(unused, event) {
                    self.showPopup('QuotationPopUpAlert', {
                        title: self.env._t('Error'),
                        body: self.env._t("Could not reach the server. Please check that you have an active internet connection, the server address you entered is valid, and the server is online."),
                    })
                    error = true;
                    return;
                }).then(async function(quotation) {
                    if (quotation) {
                        if (!error) {
                            self.env.pos.add_new_order();
                            let new_order = self.env.pos.get_order();
                            let client = self.env.pos.db.get_partner_by_id(quotation.partner_id)
                            if (quotation.partner_id && !client) {
                                await self.env.pos.load_new_partners();
                                client = self.env.pos.db.get_partner_by_id(quotation.partner_id);
                            }
                            new_order.set_client(client);
                            quotation.lines.forEach(function(line) {
                                var orderline = new pos_model.Orderline({}, {
                                    pos: self.env.pos,
                                    order: new_order,
                                    product: self.env.pos.db.get_product_by_id(line.product_id),
                                });
                                orderline.set_unit_price(line.price_unit);
                                orderline.set_discount(line.discount);
                                orderline.set_quantity(line.qty, true);
                                new_order.add_orderline(orderline);
                            });
                            let quotation_tags = {};
                            new_order.quotation_id = quotation.id;
                            new_order.quotation_name = quotation.ref;
                            new_order.seller_id = quotation.seller_id;
                            new_order.fiscal_position_id = quotation.fiscal_position_id;
                            new_order.export_as_JSON()
                            self.showPopup('QuotationPopUpAlert', {
                                title: self.env._t('Success'),
                                body: self.env._t(quotation.quotation_name + ' Loaded Successfully'),
                            })
                        }
                    }
                });
            }
        }
    });

     //define the action button
    screens.define_action_button({
        name: "LoadQuotationButton",
        widget: LoadQuotationButton,
        condition: function () {
            return this.pos;
        }
    });

});