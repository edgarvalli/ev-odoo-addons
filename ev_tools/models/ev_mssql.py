from odoo import models
from pathlib import Path
from ..services.mssql import SqlServer

class EVMssql(models.AbstractModel):
    _name = "ev.tools.mssql"
    _description = "Modulo para conectarse a Sql Server"
    
    def save_config(self, **kwargs):
        """Save Sql Server config"""
        tool = self.env["ev.tools.encrypt"].sudo()
        params = self.env["ir.config_parameter"].sudo()

        params.set_param("ev.mssql.server", kwargs.get("server", "localhost"))
        params.set_param("ev.mssql.instance", kwargs.get("instance", "SQLExpress"))
        params.set_param("ev.mssql.port", kwargs.get("port", "1433"))
        params.set_param("ev.mssql.username", kwargs.get("username", "sa"))

        password = tool.encrypt(kwargs.get("password", ""))

        params.set_param("ev.mssql.password", password)

    def get_config(self):
        tool = self.env["ev.tools.encrypt"].sudo()
        params = self.env["ir.config_parameter"].sudo()

        password = params.get_param("ev.mssql.password")

        return {
            "server": params.get_param("ev.mssql.server"),
            "instance": params.get_param("ev.mssql.instance"),
            "port": params.get_param("ev.mssql.port"),
            "username": params.get_param("ev.mssql.username"),
            "password": tool.decrypt(password) if password else "",
        }

    def connect(self, dbname="master"):
        config = self.get_mssql_config()
        return SqlServer(
            dbname=dbname,
            server=config.get("server"),
            user=config.get("username"),
            password=config.get("password"),
        )