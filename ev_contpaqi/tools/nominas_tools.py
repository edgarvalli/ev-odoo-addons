from .contpaqi_tools import get_dbname
from odoo.orm.environments import Environment


def verificar_pertenencia_comprobante(
    env: Environment, codigo: str, iddocumento: int
) -> bool:
    if not codigo or not iddocumento:
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
                        AND LOWER(LTRIM(RTRIM(e.codigoempleado))) = LOWER(?)
                )
            """
        with env["ev.tools.mssql"].connect(dbname) as db:
            result = db.fetchone(sql, (iddocumento, codigo.strip()))
            return result is not None
    except Exception:
        return False
