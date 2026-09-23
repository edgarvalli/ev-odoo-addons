from odoo.api import Environment
from odoo.exceptions import UserError

from .clientes import ComercialClientes
from .productos import ComercialProductos
from ...types.comercial_types import EmpresaDict


class EVComercial:

    def __init__(self, env: Environment):

        self.env = env

        self.clientes = ComercialClientes(env)
        self.productos = ComercialProductos(env)

    def empresas(self) -> list[EmpresaDict]:

        sql = """
            SELECT
                CIDEMPRESA id,
                CNOMBREEMPRESA empresa,
                CRUTADATOS ruta_datos,
                RIGHT(CRUTADATOS,CHARINDEX('\\', REVERSE(CRUTADATOS)) - 1) AS dbname
            FROM Empresas
            WHERE CIDEMPRESA > 1;
        """

        try:

            with self.env["ev.tools.mssql"].connect("CompacWAdmin") as db:
                return db.fetchall(sql)

        except Exception as err:
            raise UserError(str(err))
