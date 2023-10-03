odoo.define('disable_notif_update.ExpirationPanel', function(require) {
    "use strict";

    const ExpirationPanelExt = require('web_enterprise.ExpirationPanel');
    const session = require('web.session');
    const { patch } = require('web.utils');
    
    
    patch(ExpirationPanel, "ExpirationPanelExt", {
        /**
         * Save the registration code then triggers a ping to submit it.
         * @private
         */
        async _onCodeSubmit() {
            const input = this.inputRef.el;
            const enterpriseCode = input.value;
//            if (!enterpriseCode) {
//                const inputTitle = input.getAttribute("title");
//                input.setAttribute("placeholder", inputTitle);
//                return;
//            }
//            const [oldDate, , linkedSubscriptionUrl, emailLinked] = await Promise.all([
//                this.rpc({
//                    model: "ir.config_parameter",
//                    method: "get_param",
//                    args: ["database.expiration_date"],
//                }),
//                this.rpc({
//                    model: "ir.config_parameter",
//                    method: "set_param",
//                    args: ["database.enterprise_code", enterpriseCode],
//                }),
//                this.rpc({
//                    model: 'ir.config_parameter',
//                    method: 'get_param',
//                    args: ['database.already_linked_subscription_url'],
//                }),
//                this.rpc({
//                    model: 'ir.config_parameter',
//                    method: 'get_param',
//                    args: ['database.already_linked_email'],
//                })
//            ]);
//
//            this.env.services.setCookie("oe_instance_hide_panel", "", -1);
//
//            const expirationDate = await this.rpc({
//                model: "ir.config_parameter",
//                method: "get_param",
//                args: ["database.expiration_date"],
//            });

            this.env.services.unblockUI();

            this._clearState();
//            if (expirationDate !== oldDate && !linkedSubscriptionUrl) {
//                this.state.message = 'success';
//                this.state.displayRegisterForm = false;
//                this.state.alertType = "success";
//                this.state.validDate = moment(expirationDate).format("LL");
//            } else {
//                this.state.alertType = "danger";
//                this.state.buttonText = this.env._t("Retry");
//                this.state.displayRegisterForm = true;
//                if (linkedSubscriptionUrl) {
//                    this.state.message = "link";
//                    this.state.linkedSubscriptionUrl = linkedSubscriptionUrl;
//                    this.state.emailDelivery = null;
//                    this.state.emailLinked = emailLinked;
//                } else {
//                    this.state.message = 'error';
//                }
//            }
        },

        /**
         * @private
         */
        async _onCheckStatus() {
            const oldDate = await this.rpc({
                model: "ir.config_parameter",
                method: "get_param",
                args: ["database.expiration_date"],
            });

            if (this.constructor.computeDiffDays(oldDate) >= 30) {
                return;
            }

            const expirationDate = await this.rpc({
                model: "ir.config_parameter",
                method: "get_param",
                args: ["database.expiration_date"],
            });

            if (
                expirationDate !== oldDate &&
                new moment(expirationDate) > new moment()
            ) {
                this.env.services.unblockUI();
                this._clearState();
                this.state.message = 'update';
                this.state.alertType = "success";
                this.state.validDate = moment(expirationDate).format("LL");
                this.state.diffDays = this.constructor.computeDiffDays(expirationDate);
            } else {
                this.env.services.reloadPage();
            }
        },

        /**
         * @private
         */
        async _onRenew() {
            const oldDate = await this.rpc({
                model: "ir.config_parameter",
                method: "get_param",
                args: ["database.expiration_date"],
            });

            this.env.services.setCookie("oe_instance_hide_panel", "", -1);

            await this.rpc({
                model: "publisher_warranty.contract",
                method: "update_notification",
                args: [[]],
            });

            const [expirationDate, enterpriseCode] = await Promise.all([
                this.rpc({
                    model: "ir.config_parameter",
                    method: "get_param",
                    args: ["database.expiration_date"],
                }),
                this.rpc({
                    model: "ir.config_parameter",
                    method: "get_param",
                    args: ["database.enterprise_code"],
                })
            ]);

            if (
                expirationDate !== oldDate &&
                new moment(expirationDate) > new moment()
            ) {
                this.env.services.unblockUI();
                this._clearState();
                this.state.message = 'success';
                this.state.alertType = "success";
                this.state.validDate = moment(expirationDate).format("LL");
                // Same remark as above (we just want to show clear button)
                this.state.diffDays = this.constructor.computeDiffDays(expirationDate);
            } else {
                const params = enterpriseCode ? { contract: enterpriseCode } : {};
                this.env.services.navigate(
                    "https://www.odoo.com/odoo-enterprise/renew",
                    params
                );
            }
        }
    });
});
