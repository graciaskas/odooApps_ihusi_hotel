odoo.define("grc_hotel_pos.folio", function (require) {
    "use strict";

    // pos_screens
    var screens = require("point_of_sale.screens");
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var chrome = require('point_of_sale.chrome');
    var PosModelSuper = models.PosModel;
    var QWeb = core.qweb;
    var _t = core._t;
    var folios = null;
    


    //**  Load folios on start
    models.load_models({
        model: "hotel.folio",
        domain: [['state', '=', 'draft'],['product_id', '!=', false]],
        loaded: function (self, folios) {
            self.folios = folios;
            this.folios = folios;
        }
    });


    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        export_as_JSON: function () {
            var json = _super_order.export_as_JSON.apply(this, arguments);
            json.order_folio = this.order_folio;
            json.folio_id = this.folio_id;
            return json;
        },
        init_from_JSON: function (json) {
            _super_order.init_from_JSON.apply(this, arguments);
            this.order_folio = json.order_folio;
            this.folio_id = json.folio_id;
            _super_order.init_from_JSON.call(this, json);
        }
    });


    //create a new button by extending the base ActionButonWidget
    var folioButton = screens.ActionButtonWidget.extend({
        template: 'folioButton',
        button_click: function () {  //button click function
            this.gui.show_screen('folioScreenWidget'); //show folio screen
        }
    });

    //inherit Receipt screen and remove the folio selected after validation
    screens.ReceiptScreenWidget.include({
        init: function (parent, options) {
            this._super(parent, options);
        },
        click_next: function () {
            this._super();
            if (typeof window != undefined)
                window.localStorage.removeItem('pos_folio_data');
            $(".folio_content").html(`<i class="fa fa-bed"/> Room`);
        },
    });


    //create a new screen by extending the base ScreenWidget
    var folioScreenWidget = screens.ScreenWidget.extend({
        template: "folioScreenWidget",
        init: function (parent, options) {
            this._super(parent, options);
            this.folio_string = "";
            //Set current _folio on select folio button
            this.set_selected_folio();
        },

        auto_back: true,

   
        /**
         * This method will set a ui view of the selected folio
         * @param {*} folio 
         */
        set_selected_folio: function ( folio= null) {
            //Persit folio by saving its data on localStorage
            if (typeof window != undefined) {
                var folio_ = JSON.parse(window.localStorage.getItem('pos_folio_data'));
                var newFolio = null;

                //if new folio
                if ( (!folio_ && folio) || (folio_ && folio)) {
                    newFolio = JSON.stringify({
                        pos_saleman: null,
                        pos_order: null,
                        pos_session: null,
                        folio
                    });

                    //Save new folio
                    window.localStorage.setItem('pos_folio_data', newFolio);
                    //Update select pos_folio_data button to view the pos_folio_data
                    $(".folio_content")
                        .html(`<i class="fa fa-bed" data-id="${folio.id}"/> ${folio.name}`);
                } 

               //if it the folio from last order
                if (folio_ && !folio) {
                    //Update select folio button to view the folio
                    $(".folio_content")
                        .html(`<i class="fa fa-bed" data-id="${folio_.folio.id}"/> ${folio_.folio.name}`);
                }   
            }
        },

        show: function () {
            var self = this;
            var folios = this.pos.folios;
            var search_timeout = null;
            var pos = this.pos;

            const listen_click_row = function (event) {
                var row = event.target.parentNode;
                var id = row.getAttribute("data-id");
                //Get the folio object
                var folio = self.pos.folios.filter(folio => folio.id == id);
                self.folio = folio;
            
                $("tr.order-line.highlight").removeClass("highlight");  //remove all actives rows
                row.classList.add("highlight");  //set active row current row
                $(".next.oe_hidden").removeClass('oe_hidden');  //show set folio button
            };
           
            this._super();
            this.renderElement();

            this.$('.back').click(function () {
                self.gui.back();
            });

            this.render_list(folios);
           
            // try to connect the key to the search input
            if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
                this.chrome.widget.keyboard.connect(this.$('.searchbox input'));
            }

            // handler keyup event on search input
            this.$('.searchbox input').on('keyup', function (event) {
                clearTimeout(search_timeout);
                var query = this.value;
                search_timeout = setTimeout(function () {
                    self.perform_search(query, event.which === 13); // perform search

                    //listen click row select after result
                    this.$(".order-line").click(function (event) {
                        listen_click_row(event);
                    });

                }, 10);
            });

            this.$('.searchbox .search-clear').click(function () {
                self.clear_search();
            });

            //Event on click folio row select
            //highlight folio row
            //Display Set folio button
            this.$(".order-line").click(function (event) {
                listen_click_row(event); //call row click event handler
            });

            
            /** Hnadle next button after selected a folio **/
            this.$(".next").click(function () {
               
                self.set_selected_folio(self.folio[0]);  //set the selected folio
                //Get current client
                var curr_client = self.pos.get_order().get_client();
                if (curr_client) {
                    self.pos.get_order().set_client(self.pos.db.get_partner_by_id(curr_client.id));
                } else {
                    self.pos.get_order().set_client(self.pos.db.get_partner_by_id(self.folio[0].partner_id[0]));
                }
                //set order folio
                var order = self.pos.get_order();
                order.order_folio = { name: self.folio[0].name, room: self.folio[0].product_id };
                order.folio_id = self.folio[0].id;
                self.gui.back();
            });
        },


        /**
         * This method will perfom the search of a value
         * @param {*} query Search value
         * @param {*} associate_result The result associated
        */
        perform_search: function(query, associate_result){
            var new_folios;

            if(query){
                new_folios = this.search_order(query); // set new folios
                this.render_list(new_folios); // render new folios
            // if query is null or empty set folios to current folios and render them
            } else {
                var folios = this.pos.folios;
                this.render_list(folios);
            }
        },

        search_order: function(query){
            var self = this;
            var results = self.pos.folios.filter(function (folio) {
                //set to lowercase both folio name and query value
                // var folio_name_lower = folio.name.toLowerCase();
                var room_name_lower = folio.product_id.toLowerCase();
                var query_lower = query.toLowerCase();
                //return match
                return (room_name_lower.indexOf(query_lower) >= 0  );
            });
           
            var uniqueresults = [];
            $.each(results, function(i, el){
                if($.inArray(el, uniqueresults) === -1) uniqueresults.push(el);
            });
            return uniqueresults;
        },


        clear_search: function(){
            var folios = this.pos.folios;
            this.render_list(folios);
            this.$('.searchbox input')[0].value = '';
            this.$('.searchbox input').focus();
        },

        render_list: function(folios){
            var self = this;
            for(var i = 0, len = Math.min(folios.length,1000); i < len; i++) {
                if (folios[i]) {
                    var folio = folios[i];
                    self.folio_string += i + ':' + folio.company_id + '\n';
                }
            }
            var contents = this.$el[0].querySelector('.folio-list-contents');
            if (contents){
                contents.innerHTML = "";
                for(var i = 0, len = Math.min(folios.length,1000); i < len; i++) {
                    if (folios[i]) {
                        var folio = folios[i];
                        var clientline_html = QWeb.render('folioLinesScreenWidget', {
                            widget: this,
                            folio: folio
                        });
                        var folioline = document.createElement('tbody');
                        folioline.innerHTML = clientline_html;
                        folioline = folioline.childNodes[1];
                        contents.appendChild(folioline);    
                    }
                }
            }
        },


    });


  //define the folio screen
    gui.define_screen({
		name:'folioScreenWidget', 
        widget: folioScreenWidget,
        condition: function () {
            return this.pos;
        }
	});


    //define the action button
    screens.define_action_button({
        name: "folioButton",
        widget: folioButton,
        condition: function () {
            return this.pos;
        }
    });
    
});