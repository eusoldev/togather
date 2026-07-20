/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { MapArchParser } from "@web_google_maps/js/view/map/map_arch_parser";

patch(MapArchParser.prototype, {
    parse(arch) {
        const archInfo = super.parse(...arguments);
        const mapNode = arch.tagName === "google_map" ? arch : arch.querySelector("google_map");
        if (mapNode) {
            const colorField = mapNode.getAttribute("color");
            if (colorField && !archInfo.fieldNames.includes(colorField)) {
                archInfo.fieldNames.push(colorField);
            }
            // Keep consistency with what renderer expects
            archInfo.color = colorField;
        }
        return archInfo;
    }
});
