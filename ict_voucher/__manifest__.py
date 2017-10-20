# -*- coding: utf-8 -*-
#

{
    'name': 'ICTech Kế hoạch thu chi',
    'version': '1.0',
    'category': 'None',
    'summary': 'Kế hoach thu chi tổng hợp các tháng',
    'description': """
        Kế hoach thu chi tổng hợp các tháng
        
""",
    'author': 'ANHTT./',
    'website': 'http://www.ictech.vn/',
    'depends': ['base', 'web_gantt', 'account'],
    'data': [
        'views.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
