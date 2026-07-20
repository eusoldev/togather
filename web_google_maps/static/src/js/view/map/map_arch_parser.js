/** @odoo-module **/

import { visitXML } from "@web/core/utils/xml";
import { unique } from "@web/core/utils/arrays";

export class MapArchParser {
    parse(arch) {
        const archInfo = {
            fieldNames: [],
            lat: "partner_latitude",
            lng: "partner_longitude",
        };

        const mapNode = arch.tagName === "google_map" ? arch : arch.querySelector("google_map");

        if (mapNode) {
            archInfo.lat = mapNode.getAttribute("lat") || "partner_latitude";
            archInfo.lng = mapNode.getAttribute("lng") || "partner_longitude";
            archInfo.color = mapNode.getAttribute("color");
            archInfo.title = mapNode.getAttribute("title");
            archInfo.fieldNames.push(archInfo.lat, archInfo.lng);
            if (archInfo.color) archInfo.fieldNames.push(archInfo.color);
        }

        visitXML(arch, (node) => {
            if (node.tagName === "field") {
                archInfo.fieldNames.push(node.getAttribute("name"));
            }
        });

        archInfo.fieldNames = unique(archInfo.fieldNames.filter(Boolean));

        return archInfo;
    }
}
