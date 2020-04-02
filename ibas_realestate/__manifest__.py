# -*- coding: utf-8 -*-
{
    'name': "ibas_realestate",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/update_sale_price_wiz_views.xml',
        'views/views.xml',
        'views/sale.xml',
        'views/client_requirement.xml',
        'views/res_partner.xml',
        'views/templates.xml',
        'views/property_class_views.xml',
        'views/property_model_views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
