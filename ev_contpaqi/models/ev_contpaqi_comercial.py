from typing import List
from odoo.models import AbstractModel
from ..types.comercial_types import ClienteDict
from ..services import EVComercial, ContpaqiORM


class Comercial(AbstractModel):
    _name = "ev.contpaqi.comercial"
    _description = "EV Contpaqi Comercial"

    def _srv(self):
        return EVComercial(self.env)

    def _build_orm(self, tablename: str, primary_key: str):
        orm = ContpaqiORM(self.env)
        orm.TABLENAME = tablename
        orm.PRIMARY_KEY = primary_key
        orm.SISTEMA = "comercial"
        orm._build_dbname()
        return orm

    def empresas(self):
        srv = self._srv()
        return srv.empresas()

    ###### CLIENTES ######

    def clientes(
        self,
        domain: list[tuple] | None = None,
        fields: list[str] | None = None,
        limit: int = 50,
        **kwargs
    ) -> List[ClienteDict]:
        srv = self._srv()
        return srv.clientes.search(domain, fields, limit, **kwargs)

    def buscar_cliente(self, codigo: str) -> ClienteDict:
        conditions = ["c.CCODIGOCLIENTE = ?"]
        srv = self._srv()
        return srv.clientes.buscar(conditions=conditions, values=(codigo,))

    def buscar_cliente_rfc(self, rfc: str) -> ClienteDict:
        conditions = ["c.CRFC = ?"]
        srv = self._srv()
        return srv.clientes.buscar(conditions, (rfc,))

    def buscar_cliente_id(self, id: int) -> ClienteDict:
        conditions = ["c.CIDCLIENTEPROVEEDOR = ?"]
        srv = self._srv()
        return srv.clientes.buscar(conditions, (id,))

    def saldo_clientes(self, saldo_cero=True):
        """Funcion para obtener el estado de cuenta de los clientes"""
        srv = self._srv()
        return srv.clientes.saldos(saldo_cero)

    def saldo_cliente_detalle(self, **kwargs) -> ClienteDict:
        """Funcion para obtener el estado de cuenta actual del cliente"""
        srv = self._srv()
        return srv.clientes.detalle_saldos(**kwargs)

    ###### PRODUCTOS ######

    def buscar_productos(
        self,
        domain: list[tuple] | None = None,
        fields: list[str] | None = None,
        limit: int = 50,
        **kwargs
    ):
        srv = self._srv()
        return srv.productos.search(domain, fields, limit, **kwargs)

    def orm_search(
        self, tablename, primary_key, domain, offset=0, limit=50, order=None
    ):
        orm = self._build_orm(tablename, primary_key)
        return orm.search(domain, offset, limit, order)
