/** @odoo-module */

import { FormCompiler } from "@web/views/form/form_compiler";
import { patch } from "@web/core/utils/patch";

patch(FormCompiler.prototype, {
    compileHeader(el, params) {
        const statusBar = super.compileHeader(el, params);
        if (params.asDropdownItems) {
            return statusBar;
        }
        if (statusBar && typeof statusBar.querySelector === "function") {
            const statusBarButtons = statusBar.querySelector("StatusBarButtons");
            if (statusBarButtons) {
                statusBarButtons.removeAttribute("t-if");
            }
        }

        return statusBar;
    }
});
