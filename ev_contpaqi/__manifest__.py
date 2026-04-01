{
    "name": "EV Contpaqi Connector",
    "author": "Edgar Valli",
    "license": "LGPL-3",
    "description": """
        Modulo para conectar Odoo con Contpai
    """,
    "depends": ["base", "ev_tools", "hr", "sale"],
    "data": [
        "views/hr_employee_extend.xml",
        "views/res_company_extend.xml",
        "data/sync_cron.xml",
        "security/ir.model.access.csv",
        "data/actions.xml",
        "data/menu.xml",
    ],
}
