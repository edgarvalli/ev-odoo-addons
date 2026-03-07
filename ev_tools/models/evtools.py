from odoo import models
from pathlib import Path
from ..services.mssql import SqlServer
from cryptography.fernet import Fernet
from odoo.modules.module import get_module_path


class EVTools(models.AbstractModel):
    _name = "ev.tools"

    _cipher = None

    def _get_cipher(self):
        module_path = Path(get_module_path("ev_tools"))
        key_path = module_path / "private" / "evapp.key"

        key_path.parent.mkdir(parents=True, exist_ok=True)

        if key_path.exists():
            key = key_path.read_bytes()
        else:
            key = Fernet.generate_key()
            key_path.write_bytes(key)

        return Fernet(key)

    def encrypt(self, text: str):
        """Encrypt text"""
        cipher = self._get_cipher()
        return cipher.encrypt(text.encode()).decode()

    def decrypt(self, encrypted_text: str):
        """Decrypt text"""
        cipher = self._get_cipher()
        return cipher.decrypt(encrypted_text.encode()).decode()

    def save_mssql_config(self, **kwargs):
        """Save Sql Server config"""
        params = self.env["ir.config_parameter"].sudo()

        params.set_param("ev.mssql.server", kwargs.get("server", "localhost"))
        params.set_param("ev.mssql.instance", kwargs.get("instance", "SQLExpress"))
        params.set_param("ev.mssql.port", kwargs.get("port", "1433"))
        params.set_param("ev.mssql.username", kwargs.get("username", "sa"))

        password = self.encrypt(kwargs.get("password", ""))

        params.set_param("ev.mssql.password", password)

    def get_mssql_config(self):
        params = self.env["ir.config_parameter"].sudo()

        password = params.get_param("ev.mssql.password")

        return {
            "server": params.get_param("ev.mssql.server"),
            "instance": params.get_param("ev.mssql.instance"),
            "port": params.get_param("ev.mssql.port"),
            "username": params.get_param("ev.mssql.username"),
            "password": self.decrypt(password) if password else "",
        }

    def mssql(self, dbname="master"):
        config = self.get_mssql_config()
        return SqlServer(
            dbname=dbname,
            server=config.get("server"),
            user=config.get("username"),
            password=config.get("password"),
        )
