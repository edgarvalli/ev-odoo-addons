from typing import List
from dataclasses import dataclass
from odoo.orm.environments import Environment
from ..types.empleado_type import EmpleadoDict
from ..tools.contpaqi_tools import get_dbname


@dataclass
class EVEmpleadoService:
    env: Environment

    def _build_query(self, dbname: str, conditions=None, top: int = None):
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
            FROM [{dbname}].dbo.nom10001 empleado
            INNER JOIN [{dbname}].dbo.NOM10006 puesto ON puesto.idpuesto = empleado.idpuesto
            INNER JOIN [{dbname}].dbo.NOM10032 turno ON empleado.idturno = turno.idturno
            INNER JOIN [{dbname}].dbo.NOM10003 departamentos ON departamentos.iddepartamento = empleado.iddepartamento
        """

        if conditions:
            _conditions_copy = ",".join(conditions)
            sql += f" WHERE {_conditions_copy}"

        return sql

    def search(self, conditions=[], params: tuple = None) -> List[EmpleadoDict]:
        try:
            dbname = get_dbname(self.env, "nominas")
            sql = self._build_query(dbname, conditions)
            with self.env["ev.tools.mssql"].connect(dbname) as db:
                return db.fetchall(sql, tuple(params) or ())
        except Exception as e:
            raise ValueError(str(e))

    def get(self, conditions=[], params: tuple = None) -> EmpleadoDict:
        try:
            dbname = get_dbname(self.env, "nominas")
            sql = self._build_query(dbname, conditions, top=1)
            with self.env["ev.tools.mssql"].connect(dbname) as db:
                return db.fetchone(sql, tuple(params) or ())
        except Exception as e:
            raise ValueError(str(e))
