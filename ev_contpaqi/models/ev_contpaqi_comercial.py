import logging
from typing import List
from odoo.models import AbstractModel
from odoo.exceptions import UserError
from ..types.comercial_types import ClienteDict
from ..tools.contpaqi_tools import get_dbname
from ..services import EVClientesService

_logger = logging.getLogger(__name__)


class Comercial(AbstractModel):
    _name = "ev.contpaqi.comercial"
    _description = "EV Contpaqi Comercial"

    def empresas(self):
        sql = """
            SELECT
                CIDEMPRESA id,
                CNOMBREEMPRESA empresa,
                CRUTADATOS ruta_datos,
                RIGHT(CRUTADATOS,CHARINDEX('\\', REVERSE(CRUTADATOS)) - 1) AS dbname
            FROM Empresas WHERE CIDEMPRESA > 1;
        """
        try:
            with self.env["ev.tools.mssql"].connect("CompacWAdmin") as db:
                return db.fetchall(sql)
        except Exception as err:
            raise UserError(str(err))

    def clientes(self, **kwargs) -> List[ClienteDict]:
        try:
            cliente = EVClientesService(self.env)
            return cliente.search(**kwargs)
        except Exception as e:
            raise UserError(str(e))

    def buscar_cliente(self, codigo: str) -> ClienteDict:
        cliente = EVClientesService(self.env)
        conditions = ["c.CCODIGOCLIENTE = ?"]
        return cliente.get(conditions, (codigo,))

    def buscar_cliente_rfc(self, rfc: str) -> ClienteDict:
        cliente = EVClientesService(self.env)
        conditions = ["c.CRFC = ?"]
        return cliente.get(conditions, (rfc,))

    def buscar_cliente_id(self, id: int) -> ClienteDict:
        cliente = EVClientesService(self.env)
        conditions = ["c.CIDCLIENTEPROVEEDOR = ?"]
        return cliente.get(conditions, (id,))

    def saldo_clientes(self, saldo_cero=True):
        """Funcion para obtener el estado de cuenta de los clientes"""
        try:
            cliente = EVClientesService(self.env)
            return cliente.saldos(saldo_cero)
        except Exception as e:
            raise UserError(str(e))

    def saldo_cliente_detalle(self, **kwargs) -> ClienteDict:
        """Funcion para obtener el estado de cuenta actual del cliente"""
        try:
            cliente = EVClientesService(self.env)
            return cliente.detalle_saldos(**kwargs)
        except Exception as e:
            raise UserError(str(e))
