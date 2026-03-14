from odoo import models, fields
from odoo.exceptions import UserError
from ..services.mssql import SqlServer


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ev_mssql_server = fields.Char(string="SQL Server")
    ev_mssql_instance = fields.Char(string="Instance")
    ev_mssql_port = fields.Char(string="Port")
    ev_mssql_username = fields.Char(string="Username")
    ev_mssql_password = fields.Char(string="Password")

    def set_values(self):

        tools = self.env["ev.tools.mssql"]

        try:
            # probar conexión con los valores ingresados
            with SqlServer(
                dbname="master",
                server=self.ev_mssql_server,
                instance=self.ev_mssql_instance,
                user=self.ev_mssql_username,
                password=self.ev_mssql_password,
            ) as db:
                db.execute("SELECT 1")

        except Exception as e:
            raise UserError(f"No se pudo conectar a SQL Server:\n{str(e)}")

        # si pasa la prueba guarda
        super().set_values()

        tools.save_config(
            server=self.ev_mssql_server,
            instance=self.ev_mssql_instance,
            port=self.ev_mssql_port,
            username=self.ev_mssql_username,
            password=self.ev_mssql_password,
        )

    def get_values(self):
        res = super().get_values()

        config = self.env["ev.tools.mssql"].get_config()

        res.update(
            ev_mssql_server=config.server,
            ev_mssql_instance=config.instance,
            ev_mssql_port=config.port,
            ev_mssql_username=config.username,
            ev_mssql_password=config.password,
        )

        return res
