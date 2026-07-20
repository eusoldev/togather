/** @odoo-module **/

import { registry } from "@web/core/registry";
import { RelationalModel } from "@web/model/relational_model/relational_model";
import { makeActiveField } from "@web/model/relational_model/utils";
import { MapArchParser } from "./map_arch_parser";
import { MapController } from "./map_controller";
import { MapRenderer } from "./map_renderer";

export const googleMapView = {
    type: "google_map",
    display_name: "Google Map",
    icon: "fa-map-o",
    multiRecord: true,
    Controller: MapController,
    Renderer: MapRenderer,
    ArchParser: MapArchParser,
    Model: RelationalModel,

    props: (genericProps, view) => {
        const { arch, relatedModels, resModel, fields } = genericProps;
        const archInfo = new view.ArchParser().parse(arch, relatedModels, resModel);

        const activeFields = {};
        archInfo.fieldNames.forEach((name) => {
            if (fields[name]) {
                activeFields[name] = makeActiveField();
            }
        });

        const modelConfig = genericProps.state?.modelState?.config || {
            resModel,
            fields,
            activeFields,
        };

        return {
            ...genericProps,
            Model: view.Model,
            Renderer: view.Renderer,
            archInfo,
            modelParams: {
                config: modelConfig,
                state: genericProps.state?.modelState,
                limit: genericProps.limit || 80,
            },
        };
    },
};

registry.category("views").add("google_map", googleMapView);
