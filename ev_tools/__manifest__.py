{
    "name": "EV Tools",
    "version": "1.0",
    "author": "Edgar Valli",
    "description": """
        Modulo con herramiendas de desarrollo:
            - SqlServer (ev.tools.mssql)
            - Encriptacion (ev.tools)
    """,
    "depends": ["base"],
    "category": "Technical",
    "installable": True,
    "application": False,
    "license": "LGPL-3",
    "data": [
        "views/res_config_settings_view.xml",
    ],
    "external_dependencies": {
        "python": ["pyodbc"],
    },
}
