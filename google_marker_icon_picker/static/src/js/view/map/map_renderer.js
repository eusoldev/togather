/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { MapRenderer } from "@web_google_maps/js/view/map/map_renderer";

patch(MapRenderer.prototype, {
    renderMarkers(props) {
        if (this.markerCluster) {
            this.markerCluster.clearMarkers();
        }
        this.markers.forEach(m => m.setMap(null));
        this.markers = [];

        const { model, archInfo } = props;
        const records = model.root.records;
        const colorField = archInfo.color;

        records.forEach(record => {
            const lat = record.data[archInfo.lat];
            const lng = record.data[archInfo.lng];
            if (lat && lng) {
                let color = 'red';
                if (colorField && record.data[colorField]) {
                    color = record.data[colorField];
                }

                const marker = new google.maps.Marker({
                    position: { lat, lng },
                    title: record.data.display_name,
                    _odooRecord: record,
                    icon: `/web_google_maps/static/src/img/markers/${color}.png`,
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
});
