odoo.define('pos_order_quotation.DB', function(require) {
    "use strict";
    var db = require('point_of_sale.DB');

    db.include({
        init: function(options) {
            this._super.apply(this, arguments);
            this.quotations = {}
            this.quotation_by_id = {}
            this.quotation_lines = {}
            this.quotation_lines_by_id = {}
        },

        add_quotations: function(quotations) {
            var self = this;
            quotations.forEach(function(quotation) {
                self.quotation_by_id[quotation.id] = quotation;
                self.quotations[quotation.ref] = quotation;
            })
        },

        add_quotations_lines: function(quotation_lines) {
            var self = this;
            quotation_lines.forEach(function(quotation) {
                self.quotation_lines[quotation.id] = quotation;
            })
        },

        get_quotation_line_by_id: function(id) {
            return this.quotation_lines[id];
        },

        get_quotation_by_id: function(id) {
            return this.quotation_by_id[id]
        },

        get_quotation_by_ref: function(ref) {
            return this.quotations[ref]
        },

    });

    return db
});