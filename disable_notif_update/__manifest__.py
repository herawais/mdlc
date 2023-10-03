# -*- coding: utf-8 -*-
{
    'name': "Disable Notification Update",

    'summary': """
        Disable Notification Update""",

    'description': """
        Disable Cron and Webclient calls for Publisher notification update
    """,

    'author': "CodeTuple Solutions",
    'website': "http://codetuple.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mail', 'web_enterprise'],

    # always loaded
    'data': [
        'data/ir_cron_data.xml',
        'data/default_settings.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'disable_notif_update/static/src/js/expiration_panel.js',
        ]
    },
    # only loaded in demonstration mode
    'installable': True,
    'auto_install': True,
}
