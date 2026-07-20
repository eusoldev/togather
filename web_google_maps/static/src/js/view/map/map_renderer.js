/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import { Component, onWillUnmount, onMounted, onWillUpdateProps, useEffect, useRef } from "@odoo/owl";

export class MapRenderer extends Component {
    static template = "web_google_maps.MapRenderer";
    static props = ["*"];

    setup() {
        this.rootRef = useRef("map");
        this.gmap = null;
        this.markers = [];
        this.markerCluster = null;
        this.infoWindow = null;
        this.rpc = rpc;

        onMounted(() => {
            this.initMap();
        });

        onWillUpdateProps((nextProps) => {
            if (this.gmap && nextProps.model.root.records !== this.props.model.root.records) {
                this.renderMarkers(nextProps);
            }
        });

        useEffect(
            () => {
                if (this.gmap) {
                    this.renderMarkers(this.props);
                }
            },
            () => [this.props.model.root.records, this.props.archInfo]
        );

        onWillUnmount(() => {
            if (this.infoWindow) {
                this.infoWindow.close();
            }
            if (this.markerCluster) {
                this.markerCluster.clearMarkers();
            }
        });
    }

    async initMap() {
        if (!window.google || !window.google.maps) {
            console.error("Google Maps API not loaded");
            return;
        }

        this.infoWindow = new google.maps.InfoWindow();
        this.gmap = new google.maps.Map(this.rootRef.el, {
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            minZoom: 3,
            maxZoom: 20,
            fullscreenControl: true,
            mapTypeControl: true,
        });

        const data = await this.rpc("/web/map_theme");
        if (data && data.theme && data.theme !== "default") {
            const { MAP_THEMES } = await import("../../widgets/utils");
            if (MAP_THEMES && MAP_THEMES[data.theme]) {
                const styledMapType = new google.maps.StyledMapType(MAP_THEMES[data.theme], {
                    name: "Theme",
                });
                this.gmap.mapTypes.set("styled_map", styledMapType);
                this.gmap.setMapTypeId("styled_map");
            }
        }

        if (window.MarkerClusterer) {
            this.markerCluster = new MarkerClusterer(this.gmap, [], {
                imagePath: "/web_google_maps/static/lib/markercluster/img/m",
                gridSize: 20,
                maxZoom: 17,
            });
        }

        this.renderMarkers(this.props);
    }

    renderMarkers(props) {
        if (this.markerCluster) {
            this.markerCluster.clearMarkers();
        }
        this.markers.forEach(m => m.setMap(null));
        this.markers = [];

        const { model, archInfo } = props;
        const records = model.root.records;

        records.forEach(record => {
            const lat = record.data[archInfo.lat];
            const lng = record.data[archInfo.lng];
            if (lat && lng) {
                const marker = new google.maps.Marker({
                    position: { lat, lng },
                    title: record.data.display_name,
                    _odooRecord: record,
                });
                marker.addListener("click", () => {
                    this.onMarkerClick(marker, record);
                });
                this.markers.push(marker);
            }
        });

        if (this.markerCluster) {
            this.markerCluster.addMarkers(this.markers);
        } else {
            this.markers.forEach(m => m.setMap(this.gmap));
        }

        if (this.markers.length > 0) {
            const bounds = new google.maps.LatLngBounds();
            this.markers.forEach(m => bounds.extend(m.getPosition()));
            this.gmap.fitBounds(bounds);
        }
    }

    onMarkerClick(marker, record) {
        const content = document.createElement("div");
        content.innerHTML = `
            <div class="o_kanban_record" style="min-width: 200px">
                <strong>${record.data.display_name || ''}</strong>
                <div>${record.data.email || ''}</div>
                <div>${record.data.phone || ''}</div>
            </div>
        `;
        this.infoWindow.setContent(content);
        this.infoWindow.open(this.gmap, marker);
    }
}
