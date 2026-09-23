from typing import Union, List
from odoo.models import AbstractModel

from ..services.ev_nominas import EVNominas
from ..types.empleado_type import EmpleadoDict
from ..types.comprobanate_type import NominaRow, Comprobante, ComprobanteWithXML


class Nominas(AbstractModel):

    _name = "ev.contpaqi.nominas"
    _description = "EV Contpaqi Nominas"

    def _srv(self) -> EVNominas:
        return EVNominas(self.env)

    ############ EMPRESAS ############

    def empresas(self, fields: str = "*"):
        return self._srv().empresas(fields)

    def obtener_dsl(self):
        return self._srv().obtener_dsl()

    ############ EMPLEADOS ############

    def empleados(self, **kwargs):
        return self._srv().empleados.getall(**kwargs)

    def buscar_empleado(self, codigo: str) -> EmpleadoDict:

        conditions = ["empleado.codigoempleado = ?"]

        return self._srv().empleados.get(
            conditions,
            (codigo,),
        )

    def buscar_empleado_id(self, id: int) -> EmpleadoDict:

        return self._srv().empleados.get(
            ["empleado.idempleado = ?"],
            (id,),
        )

    ############ COMPROBANTES ############

    def comprobantes(
        self,
        **kwargs,
    ) -> List[Union[Comprobante, ComprobanteWithXML]]:

        return self._srv().comprobantes.search(**kwargs)

    def obtener_comprobante(
        self,
        idcomprobante,
    ) -> Union[Comprobante, ComprobanteWithXML]:

        return self._srv().comprobantes.get(idcomprobante)

    def verificar_pertenencia_comprobante(
        self,
        id: int,
        iddocumento: int,
    ) -> bool:

        return self._srv().verificar_pertenencia_comprobante(
            self.env,
            id,
            iddocumento,
        )

    def datos_comprobante(
        self,
        id_documento: int,
    ) -> NominaRow:

        return self._srv().comprobantes.get_data(id_documento)
