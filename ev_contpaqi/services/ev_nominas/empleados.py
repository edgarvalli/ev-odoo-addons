from typing import List
from odoo.api import Environment
from odoo.exceptions import UserError

from .tools import empleado_query
from ...types.empleado_type import EmpleadoDict
from ...tools.contpaqi_tools import get_dbname


class NominasEmpleados:
    def __init__(self, env: Environment):
        self.env = env
        self.dbname = get_dbname(env, "nominas")

    def _build_query(self, conditions=None, top: int = None):
        top_clause = f"TOP {top}" if top else ""
        sql = f"""
            SELECT {top_clause}
                empleado.idempleado id,
                empleado.codigoempleado codigo,
                CONCAT(empleado.nombre,' ',empleado.apellidopaterno,' ' ,empleado.apellidomaterno) AS nombre,
                CONCAT(empleado.rfc, FORMAT(empleado.fechanacimiento, 'yyMMdd') ,empleado.homoclave) as rfc,
                CONCAT(empleado.curpi, FORMAT(empleado.fechanacimiento, 'yyMMdd') ,empleado.curpf) as curp,
                empleado.fechaalta,
                empleado.numerosegurosocial,
                empleado.codigopostal,
                CASE
                    WHEN empleado.basecotizacionimss = 'F' THEN 'Fijo'
                    WHEN empleado.basecotizacionimss = 'V' THEN 'Variable'
                    WHEN empleado.basecotizacionimss = 'M' THEN 'Mixto'
                END AS tiposalario,
                CASE
                    WHEN turno.TipoJornada = 1 THEN '01 Diurna'
                    WHEN turno.TipoJornada = 2 THEN '02 Nocturna'
                    WHEN turno.TipoJornada = 3 THEN '03 Mixta'
                    WHEN turno.TipoJornada = 4 THEN '04 Por Hora'
                END AS jornada,
                puesto.descripcion puesto,
                departamentos.descripcion departamento,
                empleado.CorreoElectronico correo,
                empleado.sueldointegrado sbc,
                empleado.cidregistropatronal
                --empresa.GUIDDSL guiddsl,
                --empresa.NombreEmpresaFiscal empresa
            FROM [{self.dbname}].dbo.nom10001 empleado
            INNER JOIN [{self.dbname}].dbo.NOM10006 puesto ON puesto.idpuesto = empleado.idpuesto
            INNER JOIN [{self.dbname}].dbo.NOM10032 turno ON empleado.idturno = turno.idturno
            INNER JOIN [{self.dbname}].dbo.NOM10003 departamentos ON departamentos.iddepartamento = empleado.iddepartamento
        """

        if conditions:
            _conditions_copy = ",".join(conditions)
            sql += f" WHERE {_conditions_copy}"

        return sql

    def search(self, conditions=[], params: tuple = None) -> List[EmpleadoDict]:
        try:
            sql = self._build_query(conditions)
            with self.env["ev.tools.mssql"].connect(self.dbname) as db:
                return db.fetchall(sql, tuple(params) or ())
        except Exception as e:
            raise UserError(str(e))

    def get(self, conditions=[], params: tuple = None) -> EmpleadoDict:
        try:
            sql = self._build_query(conditions, top=1)
            with self.env["ev.tools.mssql"].connect(self.dbname) as db:
                return db.fetchone(sql, tuple(params) or ())
        except Exception as e:
            raise UserError(str(e))

    def getall(self, **kwargs):
        with self.env["ev.tools.mssql"].connect(self.dbname) as db:
            sql, args = empleado_query(self.dbname, kwargs=kwargs)
            return db.fetchall(sql, args)
