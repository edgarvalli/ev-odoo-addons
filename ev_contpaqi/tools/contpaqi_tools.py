from odoo.orm.environments import Environment
from typing import Literal


def get_dbname(
    env: Environment, sistema=Literal["contabilidad", "conmercial", "nominas"]
):

    if sistema == "comercial":
        dbname = env.company.ev_contpaqi_comercial_db.dbname or None
    elif sistema == "nominas":
        dbname = env.company.ev_contpaqi_nominas_db.dbname or None
    if not dbname:
        raise ValueError("No se ha configurado la base de datos en la compañia.")
    return dbname


def get_dsl(
    env: Environment, dbname, sis_origen=Literal["comercial", "nominas", "contabilidad"]
):

    if not sis_origen:
        raise ValueError("Debe definir el tipo de sistema de Contpaqi")

    if sis_origen == "comercial":
        sql = "SELECT CGUIDDSL guiddsl FROM admParametros;"
    elif sis_origen == "contabilidad":
        sql = "SELECT GuidDSL guiddsl FROM Parametros;"
    elif sis_origen == "nominas":
        sql = "SELECT GUIDDSL guiddsl FROM nom10000;"

    else:
        raise ValueError("Debe definir el sistema origen correcto")

    with env["ev.tools.mssql"].connect(dbname) as db:
        uid = db.fetchone(sql)

        if not uid:
            raise ValueError("No se encontro el GuidDSL")

        return uid["guiddsl"]
