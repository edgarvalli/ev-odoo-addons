from odoo.orm.environments import Environment
from typing import Literal, Union, Any


def get_dbname(
    env: Environment, sistema:Literal["contabilidad", "conmercial", "nominas"]
):

    if sistema == "comercial":
        dbname = env.company.ev_contpaqi_comercial_db.dbname or None
    elif sistema == "nominas":
        dbname = env.company.ev_contpaqi_nominas_db.dbname or None
    if not dbname:
        raise ValueError("No se ha configurado la base de datos en la compañia.")
    return dbname


def get_dsl(
    env: Union[Environment | Any], dbname, sistema:Literal["comercial", "nominas", "contabilidad"]
):

    if not sistema:
        raise ValueError("Debe definir el tipo de sistema de Contpaqi")
    
    if not dbname:
        raise ValueError("dbname es requerido")

    if sistema == "comercial":
        sql = "SELECT CGUIDDSL guiddsl FROM admParametros;"
    elif sistema == "contabilidad":
        sql = "SELECT GuidDSL guiddsl FROM Parametros;"
    elif sistema == "nominas":
        sql = "SELECT GUIDDSL guiddsl FROM nom10000;"

    else:
        raise ValueError("Debe definir el sistema origen correcto")
    
    def _get(db):
        uid = db.fetchone(sql)
        if not uid:
            raise ValueError("No se encontro el GuidDSL")

        return uid["guiddsl"]
    
    if isinstance(env, Environment):
        with env["ev.tools.mssql"].connect(dbname) as db:
            return _get(db)

    if hasattr(env, "fetchone"):
        return _get(env)

    raise TypeError("env debe ser Environment o conexión DB válida")
