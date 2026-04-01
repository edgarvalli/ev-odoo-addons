from .contpaqi_tools import get_dbname
from odoo.orm.environments import Environment


def verificar_pertenencia_comprobante(
    env: Environment,
    idempleado_contpaqi: int,
    iddocumento: int,
) -> bool:
    if not idempleado_contpaqi or not iddocumento:
        return False

    try:
        dbname = get_dbname(env, "nominas")

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

        with env["ev.tools.mssql"].connect(dbname) as db:
            result = db.fetchone(sql, (iddocumento, idempleado_contpaqi))
            return result is not None

    except Exception:
        return False
