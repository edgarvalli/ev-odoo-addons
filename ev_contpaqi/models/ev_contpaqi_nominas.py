from odoo.models import AbstractModel
from odoo.exceptions import UserError
from ..tools.sqltools import empleado_query
from ..tools.contpaqi_tools import get_dsl, get_dbname
from ..tools.nominas_tools import verificar_pertenencia_comprobante
from ..services import EVEmpleadoService, EVComprobanteService


class Nominas(AbstractModel):
    _name = "ev.contpaqi.nominas"
    _description = "EV Contpaqi Nominas"

    ### Metodos

    def empresas(self, fields: str = "*"):
        try:
            with self.env["ev.tools.mssql"].connect("nomGenerales") as db:
                sql = f"SELECT {fields} FROM NOM10000 WHERE IDEmpresa <> 1;"
                return db.fetchall(sql)
        except Exception as err:
            raise UserError(str(err))

    def obtener_dsl(self):
        dbname = get_dbname(self.env, "nominas")
        try:
            return get_dsl(self.env, dbname,"nominas")
        except Exception as err:
            raise UserError(str(err))

    def empleados(self, **kwargs):
        dbname = get_dbname(self.env, "nominas")
        with self.env["ev.tools.mssql"].connect(dbname) as db:
            sql, args = empleado_query(dbname, kwargs=kwargs)
            return db.fetchall(sql, args)

    def buscar_empleado(self, codigo: str):
        try:
            srv = EVEmpleadoService(self.env)
            return srv.get(["empleado.codigoempleado = ?"], (codigo,))
        except Exception as err:
            raise UserError(str(err))

    def buscar_empleado_id(self, id: int):
        try:
            srv = EVEmpleadoService(self.env)
            return srv.get(["empleado.idempleado"], (id,))
        except Exception as err:
            raise UserError(str(err))

    def comprobantes(self, **kwargs):
        srv = EVComprobanteService(self.env)
        return srv.nominas.comprobantes(**kwargs)
    
    def obtener_comprobante(self, idcomprobante):
        srv = EVComprobanteService(self.env)
        return srv.nominas.get_comprobante(idcomprobante)

    def verificar_pertenencia_comprobante(self, codigo: str, iddocumento: int):
        return verificar_pertenencia_comprobante(self.env, codigo, iddocumento)

    def datos_comprobante(self, id_documento: int):

        try:
            srv = EVComprobanteService(self.env)
            return srv.nominas.datos_comprobante(id_documento)
        except Exception as err:
            raise UserError(f"Error obteniendo comprobante: {err}")
