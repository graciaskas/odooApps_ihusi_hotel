odoo.define('pos_order_quotation.QuotationPopUpAlert', function(require) {
    'use strict';

    const {
        useState,
        useRef
    } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    class QuotationPopUpAlert extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            setTimeout(function() {
                $(".cancel").click();
            }, 2000);
        }
    }

    QuotationPopUpAlert.template = 'QuotationPopUpAlert';

    Registries.Component.add(QuotationPopUpAlert);
    QuotationPopUpAlert.defaultProps = {
        title: '',
        body: '',
    };
    return QuotationPopUpAlert;
});