/** @odoo-module **/

import { Layout } from "@web/search/layout";
import { SearchBar } from "@web/search/search_bar/search_bar";
import { CogMenu } from "@web/search/cog_menu/cog_menu";
import { useModelWithSampleData } from "@web/model/model";
import { standardViewProps } from "@web/views/standard_view_props";
import { Component } from "@odoo/owl";

export class MapController extends Component {
    static template = "web_google_maps.MapController";
    static components = { Layout, SearchBar, CogMenu };
    static props = {
        ...standardViewProps,
        Model: Function,
        modelParams: Object,
        Renderer: Function,
        archInfo: Object,
    };

    setup() {
        this.model = useModelWithSampleData(this.props.Model, this.props.modelParams);
    }
}
