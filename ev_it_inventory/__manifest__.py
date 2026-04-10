{
    "name": "EV IT Inventory",
    "author": "Edgar Valli",
    "license": "LGPL-3",
    "description": """
        Modulo para manejar inventario de equipos de tecnologia
    """,
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        # vistas primero
        "views/ev_inv_devices_views.xml",
        "views/ev_inv_software_views.xml",
        "views/ev_inv_license_views.xml",
        # acciones después
        "data/actions.xml",
        # menus al final
        "data/menu.xml",
    ],
    "assets": {"web.assets_backend": ["ev_it_inventory/static/src/**/*"]},
    "application": True,
    "installable": True,
}
