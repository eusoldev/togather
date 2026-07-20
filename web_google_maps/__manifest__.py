# -*- coding: utf-8 -*-
{
    'name': 'Web Google Maps',
    'version': '19.0.1.0.0',
    'author': 'Ayyan Saddiqui',
    'license': 'AGPL-3',
    'maintainer': 'Ayyan Saddiqui<ayyansaddiqui420@gmail.com>',
    'support': 'ayyansaddiqui420@gmail.com',
    'category': 'Extra Tools',
    'description': """
Web Google Map and google places autocomplete address form
==========================================================

This module brings two features:
1. Allows user to view all partners addresses on google maps.
2. Enabled google places autocomplete address form into partner
form view, provide autocomplete feature when typing address of partner
""",
    'depends': [
        'base_setup',
        'base_geolocalize',
        'web',
    ],
    'website': '',
    'data': [
        'data/google_maps_libraries.xml',
        'views/google_places_template.xml',
        'views/res_partner.xml',
        'views/res_config_settings.xml'
    ],
    'demo': [],
    'assets': {
        'web.assets_backend': [
            'web_google_maps/static/src/scss/web_maps.scss',
            'web_google_maps/static/src/scss/web_maps_mobile.scss',
            'web_google_maps/static/src/js/view/map/map_arch_parser.js',
            'web_google_maps/static/src/js/view/map/map_renderer.js',
            'web_google_maps/static/src/js/view/map/map_controller.js',
            'web_google_maps/static/src/js/view/map/map_view.js',
            'web_google_maps/static/src/js/widgets/utils.js',
            'web_google_maps/static/src/js/widgets/gplaces_autocomplete.js',
            'web_google_maps/static/src/xml/map_view_owl.xml',
            'web_google_maps/static/src/xml/widget_places.xml',
        ],
    },
    'images': ['static/description/thumbnails.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',
}
