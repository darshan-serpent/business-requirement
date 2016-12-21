# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Business Requirement Deliverable Default',
    'category': 'Business Requirements Management',
    'summary': """Manage default resource lines in your
               deliverable sales package""",
    'version': '10.0.1.0.0',
    'website': 'www.elico-corp.com',
    "author": "Elico Corp, Odoo Community Association (OCA)",
    'depends': [
        'business_requirement_deliverable',
    ],
    'data': [
        "views/business_requirement_deliverable_default.xml",
    ],
    'license': 'AGPL-3',
    'installable': True,
}
