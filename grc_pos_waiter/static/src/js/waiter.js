odoo.define("grc_pos.waiter", function (require) {
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
    var waiters = null;
    


    // // load waiters on start
    models.load_models({
        model: "hr.employee",
        domain: [['is_waiter', '=', true]],
        loaded: function (self, waiters) {
            //this = pos;
            //self = this object passed in load_model method;
            self.waiters = waiters;
            this.waiters = waiters;
        }
    });

    var _super_order = models.Order.prototype;
    
    models.Order = models.Order.extend({
        export_as_JSON: function () {
            var json = _super_order.export_as_JSON.apply(this, arguments);
            json.order_waiter = this.order_waiter;
            json.waiter_id = this.waiter_id;
            return json;
        },
        init_from_JSON: function (json) {
            _super_order.init_from_JSON.apply(this, arguments);
            this.order_waiter = json.order_waiter;
            this.waiter_id = json.waiter_id;
            _super_order.init_from_JSON.call(this, json);
        }
    });


    //create a new button by extending the base ActionButonWidget
    var waiterButton = screens.ActionButtonWidget.extend({
        template: 'waiterButton',
        //button click function
        button_click: function () {
            //show waiter screen
           this.gui.show_screen('waiterScreenWidget');
        }
    });

    //inherit Receipt screen 
    screens.ReceiptScreenWidget.include({
        init: function (parent, options) {
            this._super(parent, options);
        },
        click_next: function () {
            this._super();
            if (typeof window != undefined)
                window.localStorage.removeItem('pos_waiter_data');
            $(".waiter_content").html(`<i class="fa fa-user"/> Select Waiter`);
            
        },
    });


    //inherit Payment screen 
    screens.PaymentScreenWidget.include({
        init: function (parent, options) {
            this._super(parent, options);
            this.waiters = this.pos.waiters;
            // !this equals to this Object/Class
        },

        //validate button inherit button action
        validate_order: function(force_validation) {
            if (this.is_validOrder()) {
                this._super(force_validation);
            };
        },

        set_waiter: function (waiter) {
            var self = this;
            var order = this.pos.get_order();
            order.order_waiter = waiter.name;
            order.waiter_id = waiter.id;
           
        },

        is_validOrder: function () {
           
            var waiter = null;
            if (typeof window != undefined)
                waiter = JSON.parse(window.localStorage.getItem('pos_waiter_data'));
            
            if (!waiter) {
                this.gui.show_popup('error',{
                    'title': _t('Payment validation Error'),
                    'body': _t("\
                    We cannot validate a payment while no order's waiter is \
                    defined.Please try to select a waiter before you validate the paiement!"),
                });
                
                return false;
            } else { 
                this.set_waiter(waiter.waiter);
                return true;
            }
        }
    });


    //create a new screen by extending the base ScreenWidget
    var waiterScreenWidget = screens.ScreenWidget.extend({
        template: "waiterScreenWidget",

        init: function (parent, options) {
            this._super(parent, options);
            this.waiter_string = "";
            //Set current waiter on select waiter button
            this.set_selected_waiter();
        },
        
        auto_back: true,

        set_selected_waiter: function (waiter = null) {
            //Persit waiter by saving its data on localStorage
            if (typeof window != undefined) {
                var waiter_ = JSON.parse(window.localStorage.getItem('pos_waiter_data'));
                var newWaiter = null;

                //if new waiter
                if ( (!waiter_ && waiter) || (waiter_ && waiter)) {
                    newWaiter = JSON.stringify({
                        pos_saleman: null,
                        pos_order: null,
                        pos_session: null,
                        waiter
                    });
                    //Save new waiter
                    window.localStorage.setItem('pos_waiter_data', newWaiter);
                    //Update select waiter button to view the waiter
                    $(".waiter_content")
                        .html(`<i class="fa fa-user" data-id="${waiter.id}"/> ${waiter.name}`);
                } 

               //if it the waiter from last order
                if (waiter_ && !waiter) {
                    //Update select waiter button to view the waiter
                    $(".waiter_content")
                        .html(`<i class="fa fa-user" data-id="${waiter_.waiter.id}"/> ${waiter_.waiter.name}`);
                }   
            }
           
        },

        show: function () {
            var self = this;
            var waiters = this.pos.waiters;
            var search_timeout = null;
            var pos = this.pos;
           
            this._super();
            this.renderElement();

            this.$('.back').click(function () {
                self.gui.back();
            });

            this.render_list(waiters);
           
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
                }, 70);
            });

            this.$('.searchbox .search-clear').click(function () {
                self.clear_search();
            });

            //Event on click waiter row select
            //highlight waiter row
            //Display Set waiter button
            this.$(".order-line").click(function (event) {
                var row = event.target.parentNode;
                var id = row.getAttribute("data-id");
                //Get the waiter object
                var waiter = waiters.filter(waiter => waiter.id == id);
                self.waiter = waiter;
                //remove all actives rows
                $("tr.order-line.highlight").removeClass("highlight");
                //set active row current row
                row.classList.add("highlight");
                //show set waiter button
                $(".next.oe_hidden").removeClass('oe_hidden');
            });

            
            /** Set waiter button clicked **/
            this.$(".next").click(function () {
                self.set_selected_waiter(self.waiter[0]);
                self.gui.back();
            });
        },


        /**
         * This method will perfom the search of a value
         * @param {*} query Search value
         * @param {*} associate_result The result associated
        */
        perform_search: function(query, associate_result){
            var new_waiters;

            if(query){
                new_waiters = this.search_order(query); // set new waiters
                this.render_list(new_waiters); // render new waiters

            // if query is null or empty set waiters to current waiters and render them
            } else {
                var waiters = this.pos.waiters;
                this.render_list(waiters);
            }
        },

        search_order: function(query){
            var self = this;
            var results = self.pos.waiters.filter(function (waiter) {
                //set to lowercase both waiter name and query value
                var waiter_name_lower = waiter.name.toLowerCase();
                var query_lower = query.toLowerCase();
                //return match
                return (waiter_name_lower.indexOf(query_lower) >= 0);
            });
           
            var uniqueresults = [];
            $.each(results, function(i, el){
                if($.inArray(el, uniqueresults) === -1) uniqueresults.push(el);
            });
            return uniqueresults;
        },


        clear_search: function(){
            var waiters = this.pos.waiters;
            this.render_list(waiters);
            this.$('.searchbox input')[0].value = '';
            this.$('.searchbox input').focus();
        },


        line_select: function(event,$line,id){
           
        },


        render_list: function(waiters){
            var self = this;
            for(var i = 0, len = Math.min(waiters.length,1000); i < len; i++) {
                if (waiters[i]) {
                    var waiter = waiters[i];
                    self.employee_string += i + ':' + waiter.company_id + '\n';
                }
            }
            var contents = this.$el[0].querySelector('.waiter-list-contents');
            if (contents){
                contents.innerHTML = "";
                for(var i = 0, len = Math.min(waiters.length,1000); i < len; i++) {
                    if (waiters[i]) {
                        var waiter = waiters[i];
                        var clientline_html = QWeb.render('waiterLinesScreenWidget', {
                            widget: this,
                            waiter: waiter
                        });
                        var waiterline = document.createElement('tbody');
                        waiterline.innerHTML = clientline_html;
                        waiterline = waiterline.childNodes[1];
                        contents.appendChild(waiterline);    
                    }
                }
            }
        },

    });



    //define the waiter screen
    gui.define_screen({
		name:'waiterScreenWidget', 
        widget: waiterScreenWidget,
        condition: function () {
            return this.pos;
        }
	});


    //define the waiter button
    screens.define_action_button({
        name: "waiter_button",
        widget: waiterButton,
        condition: function () {
            return this.pos;
        }
    });

    return {
        waiterScreenWidget: waiterScreenWidget
    }
});