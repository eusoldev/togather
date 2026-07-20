# -*- coding: utf-8 -*-
{
    'name': 'Google Marker Icon Picker',
    'version': '19.0.1.0.0',
    'author': 'Ayyan Saddiqui',
    'license': 'AGPL-3',
    'maintainer': 'Ayyan Saddiqui<ayyansaddiqui420@gmail.com>',
    'support': 'ayyansaddiqui420@gmail.com',
    'category': 'Extra Tools',
    'description': """
Google Marker Icon Picker
=========================
- New widget `google_marker_picker` allowing user to assign marker's color
  manually. To apply the selecter marker on map, you can tell map view by
  adding attribute color='[field_name]'
""",
    'depends': ['web_google_maps'],
    'website': '',
    'data': [],
    'demo': [],
    'assets': {
        'web.assets_backend': [
            'google_marker_icon_picker/static/src/js/widget/field_marker.js',
            'google_marker_icon_picker/static/src/js/view/map/map_arch_parser.js',
            'google_marker_icon_picker/static/src/js/view/map/map_renderer.js',
            'google_marker_icon_picker/static/src/xml/marker_color.xml',
        ],
    },
    'installable': True,
}
