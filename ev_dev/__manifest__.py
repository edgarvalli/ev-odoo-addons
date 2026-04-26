{
    "name": "EV Dev",
    "version": "1.0",
    "category": "CRM",
    "author": "Edgar Valli",
    "license": "LGPL-3",
    "summary": "Modulo para pruebas de desarrollo",
    "depends": ["base", "web"],
    "data": ["data/menu.xml", "security/ir.model.access.csv", "views/ev_dev_form.xml"],
    "assets": {
        "web.assets_backend": [
            "ev_dev/static/src/widgets/**/*",
            "ev_dev/static/src/register.js",
        ]
    },
    "installable": True,
    "auto_install": False,
}
