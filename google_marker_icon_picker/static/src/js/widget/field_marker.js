/** @odoo-module **/

import { registry } from "@web/core/registry";
import { CharField, charField } from "@web/views/fields/char/char_field";
import { useState } from "@odoo/owl";

export class MarkerColorPicker extends CharField {
    static template = "google_marker_icon_picker.MarkerColorPicker";

    setup() {
        super.setup();
        this.state = useState({
            open: false,
        });
    }

    get colors() {
        return [
            ['black', 'black', 'Black'], ['blue', 'blue', 'Blue'], ['brown', 'brown', 'Brown'],
            ['cyan', 'cyan', 'Cyan'], ['fuchsia', 'fuchsia', 'Fuchsia'], ['green', 'green', 'Green'],
            ['grey', 'grey', 'Grey'], ['lime', 'lime', 'Lime'], ['maroon', 'maroon', 'Maroon'],
            ['navy', 'navy', 'Navy'], ['olive', 'olive', 'Olive'], ['orange', 'orange', 'Orange'],
            ['pink', 'pink', 'Pink'], ['purple', 'purple', 'Purple'], ['red', 'red', 'Red'],
            ['teal', 'teal', 'Teal'], ['white', 'white', 'White'], ['yellow', 'yellow', 'Yellow']
        ];
    }

    onSelectColor(color) {
        this.props.record.update({ [this.props.name]: color });
    }
}

export const markerColorPicker = {
    ...charField,
    component: MarkerColorPicker,
};

registry.category("fields").add("google_marker_picker", markerColorPicker);
