# -*- coding: utf-8 -*-
{
    'name': "l10n_fr_ebics",

    'summary': """Implementation of the  EBICS banking protocol""",

    'description': """
        This module provides an interface to echanges files with banks. It's curently a beta version.
		
		This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    """,

    'author': "Aurélien DUMAINE - aurelien.dumaine@free.fr",
    'website': "http://www.dumaine.me",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
		'views/ebics.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}
