/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { useInputField } from "@web/views/fields/input_field_hook";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, onMounted, onWillUnmount, useRef } from "@odoo/owl";
import { gmaps_populate_address, gmaps_populate_places, fetchValues, fetchCountryState } from "./utils";

const IND_MAPPING = {
    ind_street: ['street_number', 'route'],
    ind_street2: ['administrative_area_level_3', 'administrative_area_level_4', 'administrative_area_level_5'],
    ind_city: ['locality', 'administrative_area_level_2'],
    ind_zip: 'postal_code',
    ind_state_id: 'administrative_area_level_1',
    ind_country_id: 'country',
};

export class GplaceAddressAutocompleteField extends Component {
    static template = "web_google_maps.GplaceAddressAutocompleteField";
    static props = {
        ...standardFieldProps,
        autocomplete: { type: String, optional: true },
        isPassword: { type: Boolean, optional: true },
        placeholder: { type: String, optional: true },
        options: { type: Object, optional: true },
    };

    setup() {
        this.inputRef = useRef("input");
        this.rpc = rpc;
        this.orm = useService("orm");
        this.autocomplete = null;
        useInputField({
            getValue: () => this.props.record.data[this.props.name] || "",
            parse: (value) => value,
            ref: this.inputRef,
        });

        onMounted(() => {
            if (this.props.readonly) return;
            this.initAutocomplete();
        });

        onWillUnmount(() => {
            if (this.autocomplete) {
                google.maps.event.clearInstanceListeners(this.autocomplete);
            }
        });
    }

    get autocompleteConfig() {
        return {
            types: ["address"],
            fields: ["address_components", "name", "geometry"],
        };
    }

    get addressOptions() {
        return {
            street: ['street_number', 'route'],
            street2: ['administrative_area_level_3', 'administrative_area_level_4', 'administrative_area_level_5'],
            city: ['locality', 'administrative_area_level_2'],
            zip: 'postal_code',
            state_id: 'administrative_area_level_1',
            country_id: 'country',
        };
    }

    async initAutocomplete() {
        if (!window.google || !window.google.maps || !window.google.maps.places) {
            console.error("Google Places API not loaded");
            return;
        }

        const settings = await this.rpc("/web/google_autocomplete_conf");

        this.autocomplete = new google.maps.places.Autocomplete(this.inputRef.el, {
            ...this.autocompleteConfig,
            ...settings
        });

        this.autocomplete.addListener("place_changed", () => {
            this.onPlaceChanged();
        });
    }

    async onPlaceChanged() {
        const place = this.autocomplete.getPlace();
        console.log("Autocomplete Place Result:", place);
        if (!place.address_components) {
            console.warn("No address components found in place result");
            return;
        }

        const options = this.props.options || {};
        const fillfields = { ...this.addressOptions, ...(options.fillfields || {}) };
        for (const [indField, googleFields] of Object.entries(IND_MAPPING)) {
            if (this.props.record.fields[indField] && !fillfields[indField]) {
                fillfields[indField] = googleFields;
            }
        }

        console.log("Widget Options:", options);
        console.log("Record Fields:", this.props.record.fields);

        const changes = gmaps_populate_address(place, fillfields);

        if (place.geometry && place.geometry.location) {
            const latField = options.lat || "partner_latitude";
            const lngField = options.lng || "partner_longitude";

            const lat = typeof place.geometry.location.lat === 'function' ? place.geometry.location.lat() : place.geometry.location.lat;
            const lng = typeof place.geometry.location.lng === 'function' ? place.geometry.location.lng() : place.geometry.location.lng;

            console.log("Geolocation Values Caught:", lat, lng);

            if (this.props.record.fields[latField]) {
                changes[latField] = lat;
            } else {
                console.warn(`Field ${latField} not found in record fields. Make sure it is in the view.`);
            }
            if (this.props.record.fields[lngField]) {
                changes[lngField] = lng;
            } else {
                console.warn(`Field ${lngField} not found in record fields. Make sure it is in the view.`);
            }
        }

        // Handle relational fields
        for (const [field, value] of Object.entries(changes)) {
            const fieldInfo = this.props.record.fields[field];
            if (fieldInfo && fieldInfo.type === 'many2one' && value && typeof value === 'string') {
                if (field === 'state_id' || field.endsWith('state_id')) {
                    const countryField = options.fillfields?.country_id || 'country_id';
                    const countryIdValue = changes[countryField] || this.props.record.data[countryField];
                    const countryId = Array.isArray(countryIdValue) ? countryIdValue[0] : countryIdValue;

                    const state = await fetchCountryState(this.orm, fieldInfo.relation, countryId, value);
                    if (state.id) {
                        changes[field] = [state.id, state.display_name];
                    } else {
                        delete changes[field];
                    }
                } else {
                    const val = await fetchValues(this.orm, fieldInfo.relation, field, value);
                    if (val[field]) {
                        changes[field] = [val[field].id, val[field].display_name];
                    } else {
                        delete changes[field];
                    }
                }
            }
        }

        console.log("Applying Changes to Record:", changes);
        await this.props.record.update(changes);
    }
}

export class GplacesAutocompleteField extends GplaceAddressAutocompleteField {
    get autocompleteConfig() {
        return {
            types: ["establishment"],
            fields: ["address_components", "name", "website", "geometry", "international_phone_number", "formatted_phone_number"],
        };
    }

    get generalOptions() {
        return {
            name: 'name',
            website: 'website',
            phone: ['international_phone_number', 'formatted_phone_number']
        };
    }

    async onPlaceChanged() {
        const place = this.autocomplete.getPlace();
        console.log("Establishment Autocomplete Place Result:", place);
        if (!place.address_components) {
            console.warn("No address components found in establishment place result");
            return;
        }

        const options = this.props.options || {};
        const fillfields = options.fillfields || {};

        console.log("Establishment Widget Options:", options);
        console.log("Record Fields:", this.props.record.fields);

        const addressFill = { ...this.addressOptions, ...(fillfields.address || {}) };
        const generalFill = { ...this.generalOptions, ...(fillfields.general || {}) };

        // Automatically add ind_ fields mapping to addressFill if they exist on the record
        for (const [indField, googleFields] of Object.entries(IND_MAPPING)) {
            if (this.props.record.fields[indField] && !addressFill[indField]) {
                addressFill[indField] = googleFields;
            }
        }

        const changes = {
            ...gmaps_populate_address(place, addressFill),
            ...gmaps_populate_places(place, generalFill),
        };

        if (place.geometry && place.geometry.location) {
            const geolocation = fillfields.geolocation || {};
            const lat = typeof place.geometry.location.lat === 'function' ? place.geometry.location.lat() : place.geometry.location.lat;
            const lng = typeof place.geometry.location.lng === 'function' ? place.geometry.location.lng() : place.geometry.location.lng;

            console.log("Establishment Geolocation Values Found:", lat, lng);
            console.log("Geolocation Mapping Options:", geolocation);

            for (const [field, alias] of Object.entries(geolocation)) {
                if (this.props.record.fields[field]) {
                    if (alias === 'latitude') {
                        changes[field] = lat;
                    } else if (alias === 'longitude') {
                        changes[field] = lng;
                    }
                } else {
                    console.warn(`Geolocation target field ${field} not found in record fields`);
                }
            }
        }

        // Handle relational fields
        for (const [field, value] of Object.entries(changes)) {
            const fieldInfo = this.props.record.fields[field];
            if (fieldInfo && fieldInfo.type === 'many2one' && value && typeof value === 'string') {
                if (field === 'state_id' || field.endsWith('state_id')) {
                    const countryField = fillfields.address?.country_id || 'country_id';
                    const countryIdValue = changes[countryField] || this.props.record.data[countryField];
                    const countryId = Array.isArray(countryIdValue) ? countryIdValue[0] : countryIdValue;

                    const state = await fetchCountryState(this.orm, fieldInfo.relation, countryId, value);
                    if (state.id) {
                        changes[field] = [state.id, state.display_name];
                    } else {
                        delete changes[field];
                    }
                } else {
                    const val = await fetchValues(this.orm, fieldInfo.relation, field, value);
                    if (val[field]) {
                        changes[field] = [val[field].id, val[field].display_name];
                    } else {
                        delete changes[field];
                    }
                }
            }
        }

        console.log("Applying Establishment Changes to Record:", changes);
        await this.props.record.update(changes);
    }
}

export const gplaceAddressAutocompleteField = {
    component: GplaceAddressAutocompleteField,
    displayName: "Google Address Autocomplete",
    supportedTypes: ["char", "text"],
    extractProps: ({ attrs, options, placeholder }) => ({
        autocomplete: attrs.autocomplete,
        isPassword: false,
        options,
        placeholder,
    }),
};

export const gplacesAutocompleteField = {
    component: GplacesAutocompleteField,
    displayName: "Google Places Autocomplete",
    supportedTypes: ["char", "text"],
    extractProps: ({ attrs, options, placeholder }) => ({
        autocomplete: attrs.autocomplete,
        isPassword: false,
        options,
        placeholder,
    }),
};

registry.category("fields").add("gplaces_address_autocomplete", gplaceAddressAutocompleteField);
registry.category("fields").add("gplaces_autocomplete", gplacesAutocompleteField);