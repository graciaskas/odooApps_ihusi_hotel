odoo.define("pos.quotation", function(require) {
    var models = require('point_of_sale.models');

    var _super_pos = models.PosModel.prototype;
    _super_pos.models.push({
        model: 'pos.quotation',
        label: 'load_quotations',
        fields: ['name', 'pos_session_id', 'company_id', 'config_id', 'quotation_date', 'ref', 'user_id',
            'amount_tax', 'amount_total', 'pricelist_id', 'partner_id', 'fiscal_position_id', 'write_date',
            'notes', 'currency_id', 'lines'
        ],
        domain: function(self) {
            return [
                ['company_id', '=', self.company.id],
                ['state', '=', 'draft']
            ];
        },
        loaded: function(self, quotations) {
            self.quotations = quotations;
            self.db.add_quotations(quotations);
        },
    });
    _super_pos.models.push({
        model: 'pos.quotation.line',
        label: 'load_quotations_line',
        fields: ['company_id', 'product_id', 'price_unit', 'qty', 'price_subtotal', 'price_subtotal_incl',
            'discount', 'quotation_id', 'product_uom_id', 'currency_id', 'tax_ids'
        ],
        domain: function(self) {
            return [
                ['company_id', '=', self.company.id]
            ];
        },
        loaded: function(self, quotations_line) {
            self.quotations_line = quotations_line;
            self.db.add_quotations_lines(quotations_line);
        },
    });

    models.PosModel = models.PosModel.extend({
        initialize: function(attributes, options) {
            _super_pos.initialize.apply(this, arguments);
        },
    });


    var _super_pos_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attributes, options) {
            _super_pos_order.initialize.apply(this, arguments);
            return this;
        },
        export_as_JSON: function() {
            let json = _super_pos_order.export_as_JSON.apply(this, arguments);
            json.quotation_id = this.quotation_id;
            json.quotation_name = this.quotation_name;
            json.seller_id = this.seller_id;
            json.seller_id = this.seller_id;
            return json;
        },

        export_for_printing: function() {
            var self = this;
            var receipt = _super_pos_order.export_for_printing.apply(this, arguments);
            if (this.seller_id) {
                const user = self.pos.users.find((user) => user.id = self.seller_id);
                if (user) {
                    receipt['seller'] = user.name
                }
            }
            if (this.quotation_id) {
                var quotation = this.pos.db.get_quotation_by_id(this.quotation_id)
                if (quotation) {
                    receipt['quotation'] = {
                        name: quotation.ref,
                        id: quotation.id,
                        customer: quotation.partner_id ? quotation.partner_id[2] : ''
                    }
                }
            }
            return receipt
        }
    });

});