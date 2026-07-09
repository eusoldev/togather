# -*- coding: utf-8 -*-
{
    'name': "Travel Agency CRM: Unified Workflow",
    'summary': "Seamless integration between CRM Leads, Quotation Builder, and Travel Reservations.",
    'description': """
Travel Agency CRM Integration
=============================
This module optimizes the Odoo 18 CRM Lead workflow specifically for Travel Agencies.

Key Features:
-------------
* **Bidirectional Navigation**: Smart buttons on CRM Leads, Quotation Builders, and Reservations (Sale Orders).
* **Financial Sync**: Sums 'Package Total' from travel reservations directly into the CRM Lead's 'Actual Revenue'.
* **Enriched Kanban**: View Trip Dates, Destination, Guests, and Quotation/Reservation numbers directly on the Kanban card.
* **Smart Information Mapping**: Automated branch and trip data inheritance during creation of quotes and reservations.
* **UI Refinements**: Specialized Form headers for Budget and Revenue, and integrated Marketing Source/Medium/Campaign tracking.
    """,
    'author': "Yasir Iqbal / Antigravity",
    'website': "eusol.net",
    'category': 'Sales/CRM',
    'license': 'LGPL-3',
    'version': '1.0',
    'depends': [
        'base', 
        'crm', 
        'sale_crm', 
        'travel_package', 
        'quotation_builder'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/static.xml',
        'views/views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
