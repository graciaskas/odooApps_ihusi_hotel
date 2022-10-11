odoo.define("pos_order_quotation.LoadQuotationPopup", function(require) {
    "use strict";

    const {
        useState,
        useRef
    } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const {
        useListener
    } = require('web.custom_hooks');

    class LoadQuotationPopup extends AbstractAwaitablePopup {

        constructor() {
            super(...arguments);
            var self = this;
            this.selectedQuoteId = null;
            this.selectedQuote = null;
            this.state = useState({
                quotations: []
            });
            this.inputRef = useRef('input');
            this.dropDownRef = useRef('drop-down')
            this.currentQuotationRef = useRef('current_quotation');
            this.widget = useState({
                customer: null,
                quotation_date: null,
                amount_total: null,
                status: null,
                notes: null
            });
            useListener('select-quote', this.selectQuote);
        }
        mounted() {
            let self = this;
            $(this.inputRef.el).on('change', self.fetchQuotations.bind(self))
        }

        selectQuote(event) {
            const {
                selectedQuoteId,
                selectedQuote
            } = event.detail;
            this.selectQuoteId = selectedQuoteId;
            this.selectedQuote = selectedQuote;
            this.widget.customer = this.selectedQuote ? this.selectedQuote.partner_id[2] : '';
            this.widget.notes = this.selectedQuote.notes;
            this.widget.status = this.selectedQuote.state;
            this.widget.quotation_date = this.selectedQuote.quotation_date;
            this.widget.amount_total = this.selectedQuote.amount_total;
            $(this.inputRef.el).val(this.selectedQuote.ref);
            $(this.dropDownRef.el).hide();
            $(this.currentQuotationRef.el).show()
        }

        async fetchQuotations(event) {
            $(this.currentQuotationRef.el).hide()
            $(this.dropDownRef.el).show();
            const {
                quotations
            } = await this._fetchQuotations(event.currentTarget.value)
            if (quotations) {
                this.state.quotations = quotations;
                this.env.pos.db.add_quotations(quotations);
            }
        }

        getPayload() {
            return this.selectedQuote;
        }

        async confirm() {
            if (!this.selectedQuote) {
                this.showPopup('QuotationPopUpAlert', {
                    title: this.env._t('Message'),
                    body: this.env._t("No Quotation Loaded. Please select a quotation to load"),
                });
                return;
            }
            this.props.resolve({
                confirmed: true,
                payload: await this.getPayload()
            });
            this.trigger('close-popup');
        }

        _fetchQuotations(inputValue) {
            var self = this;
            return new Promise(function(resolve, reject) {
                if (!inputValue) {
                    resolve({
                        'quotations': []
                    });
                    return;
                }
                let domain = [
                    ['company_id', '=', self.env.pos.company.id],
                    ['ref', 'ilike', self.props.value],
                    ['state', '=', 'draft']
                ]
                self.rpc({
                    model: 'pos.quotation',
                    method: 'search_read',
                    args: [domain],
                }).catch(function(unused, event) {
                    self.showPopup('QuotationPopUpAlert', {
                        title: self.env._t('Error'),
                        body: self.env._t("Could not reach the server. Please check that you have an active internet connection, the server address you entered is valid, and the server is online."),
                    });
                    return;
                }).then(function(quotations) {
                    if (quotations) quotations.reverse()
                    resolve({
                        'quotations': quotations
                    });
                });
            });
        }
    }
    LoadQuotationPopup.template = 'LoadQuotationPopUp';
    LoadQuotationPopup.defaultProps = {
        title: 'Confirm ?',
        value: '',
    };
    Registries.Component.add(LoadQuotationPopup);

    return LoadQuotationPopup;
});