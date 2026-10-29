{
    "name": "EV - Mesa de Ayuda TI",
    "version": "1.0.0",
    "summary": "Gestión de tickets de soporte técnico",
    "category": "Services",
    "author": "EV IT",
    "license": "LGPL-3",
    "depends": ["base", "mail", "ev_assets"],
    "data": [
        "data/groups.xml",
        "data/searchs.xml",
        "data/actions.xml",
        "data/menu.xml",
        "data/ir_sequence_data.xml",
        "data/helpdesk_stage_data.xml",
        "security/ir.model.access.csv",
        "templates/ticket_template.xml",
        "views/helpdesk_ticket_views.xml",
        # Pages
        "pages/portal_index.xml",
    ],
    "installable": True,
    "application": True,
}
