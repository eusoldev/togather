/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted } from "@odoo/owl";

export class PasswordClientAction extends Component {
    setup() {
        this.action = useService("action");
        onMounted(() => {
            this.openPopup();
        });
    }
    async openPopup() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: "Password Confirmation",
            res_model: "password.confirmations",
            view_mode: "form",
            views: [[false, "form"]],
            target: "new",
        });
    }

}

PasswordClientAction.template = "password_module.PasswordClientAction";

registry.category("actions").add("client_action_tag_custom", PasswordClientAction);
