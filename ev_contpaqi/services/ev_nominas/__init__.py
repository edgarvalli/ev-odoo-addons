from odoo.api import Environment
from odoo.exceptions import UserError
from .empleados import NominasEmpleados
from .sync_job_title import SyncJobTitle
from .sync_employees import SyncEmployees
from .comprobantes import NominasComprobante
from .sync_departments import SyncDepartments
from .tools import verificar_pertenencia_comprobante
from ...tools.contpaqi_tools import get_dbname, get_dsl


class EVNominas:

    def __init__(self, env: Environment):
        self.env = env
        self.comprobantes = NominasComprobante(env)
        self.empleados = NominasEmpleados(env)
        self.job_title = SyncJobTitle(env)
        self.department = SyncDepartments(env)
        self.employees = SyncEmployees(env)

    def empresas(self, fields: str = "*") -> list[dict]:
        try:
            with self.env["ev.tools.mssql"].connect("nomGenerales") as db:
                sql = f"SELECT {fields} FROM NOM10000 WHERE IDEmpresa <> 1;"
                return db.fetchall(sql)
        except Exception as err:
            raise UserError(str(err))

    def obtener_dsl(self):
        dbname = get_dbname(self.env, "nominas")
        try:
            return get_dsl(self.env, dbname, "nominas")
        except Exception as err:
            raise UserError(str(err))

    def verificar_pertenencia_comprobante(
        self,
        idempleado: int,
        iddocumento: int,
    ) -> bool:

        if not idempleado or not iddocumento:
            return False

        try:
            dbname = get_dbname(self.env, "nominas")

            sql = f"""
                SELECT 1
                FROM [{dbname}].dbo.nom10043 c
                WHERE c.IdDocumento = ?
                AND EXISTS (
                    SELECT 1
                    FROM [{dbname}].dbo.nom10001 e
                    WHERE e.idempleado = c.IdEmpleado
                    AND e.idempleado = ?
                )
            """

            with self.env["ev.tools.mssql"].connect(dbname) as db:
                result = db.fetchone(sql, (iddocumento, idempleado))
                return result is not None

        except Exception:
            return False
