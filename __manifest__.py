# -*- coding: utf-8 -*-
{
    'name': 'com',
    'version': '18.0.1.0.0',
    'author': 'SMK Group',
    'category': 'Tools',
    'summary': 'Интеграция Компасс',
    'description': """ """,
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/main_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'com/static/dist/js/vue-app.iife.js',
            'com/static/dist/css/vue-app.css',
            'com/static/src/js/vue_integration.js',
            'com/static/src/xml/vue_template.xml',
            'com/static/src/css/app.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}