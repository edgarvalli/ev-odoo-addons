from typing import List
from dataclasses import dataclass
from ..tools.sqltools import get_pagination
from ..tools.contpaqi_tools import get_dbname
from odoo.orm.environments import Environment
from ..types.comercial_types import ClienteDict


@dataclass
class EVClientesService:
    env: Environment

    #### HELPERS ####

    def _build_conditions(self, **kwargs):
        args = []
        conditions = ["c.CIDCLIENTEPROVEEDOR > 1"]

        if "q" in kwargs:
            conditions.append(
                "(c.CCODIGOCLIENTE LIKE ? OR c.CRAZONSOCIAL LIKE ? OR c.CRFC LIKE ?)"
            )
            q = kwargs["q"] + "%"
            args.extend([q, q, q])

        return conditions, args

    def _build_sql_cliente(self, conditions: List[str] = None, top: int = None):
        top_clause = f"TOP {top}" if top else ""
        if conditions:
            conditions_copy = " AND ".join(conditions)
            where_clause = f" WHERE {conditions_copy}"

        return f"""
            SELECT {top_clause}
                c.CIDCLIENTEPROVEEDOR id,
                c.CCODIGOCLIENTE codigo,
                c.CRAZONSOCIAL razon_social,
                c.CFECHAALTA fecha_alta,
                c.CFECHABAJA fecha_baja,
                c.CRFC rfc,
                c.CCURP curp,
                CONCAT_WS(',',
                    NULLIF(TRIM(c.CEMAIL1), ''),
                    NULLIF(TRIM(c.CEMAIL2), ''),
                    NULLIF(TRIM(c.CEMAIL3), '')
                ) AS emails,
                m.CIDMONEDA [moneda.id],
                m.CNOMBREMONEDA [moneda.nombre],
                m.CCLAVESAT [moneda.clave_sat],
                m.CSIMBOLOMONEDA [moneda.sombolo],
                cv.CVALORCLASIFICACION [clasificacion.valor],
                cv.CCODIGOVALORCLASIFICACION [clasificacion.codigo]
            FROM admClientes c
            INNER JOIN admMonedas m ON m.CIDMONEDA = c.CIDMONEDA
            INNER JOIN admClasificacionesValores cv ON cv.CIDVALORCLASIFICACION = c.CIDVALORCLASIFCLIENTE1
            {where_clause if conditions else ""}
        """

    def _build_conditions_saldo(self, **kwargs):
        conditions = []
        args = []
        conditions_cliente = []
        args_cliente = []

        idcliente = kwargs.get("id")
        if not idcliente:
            codigo_cliente = kwargs.get("codigo")

            if not codigo_cliente:
                raise ValueError("Debe de definir id:int o codigo:str")

            conditions.append("doc.CCODIGOCLIENTE = ?")
            args.append(codigo_cliente)

            conditions_cliente.append("c.CCODIGOCLIENTE = ?")
            args_cliente.append(codigo_cliente)

        else:
            conditions.append("doc.CIDCLIENTEPROVEEDOR = ?")
            args.append(idcliente)

            conditions_cliente.append("c.CIDCLIENTEPROVEEDOR = ?")
            args_cliente.append(idcliente)

        saldo_cero = kwargs.get("saldo_cero")

        if not saldo_cero:
            conditions.append("doc.CPENDIENTE > 0")

        return conditions, args, conditions_cliente, args_cliente

    def _buil_sql_saldo_detalle(self, conditions: List[str]):
        return f"""
            DECLARE @today DATE = CAST(GETDATE() AS DATE);

            SELECT
                doc.CIDDOCUMENTO id_documento,
                doc.CSERIEDOCUMENTO serie,
                doc.CFOLIO folio,
                CONCAT(doc.CSERIEDOCUMENTO, ' ',doc.CFOLIO) serie_folio,
                doc.CFECHA fecha,
                --doc.CRAZONSOCIAL razon_social,
                --doc.CRFC rfc,
                doc.CFECHAVENCIMIENTO fecha_vencimiento,
                doc.COBSERVACIONES observaciones,
                doc.CREFERENCIA referencia,
                folios.CUUID uuid,
                CASE
                    WHEN DATEDIFF(DAY,doc.CFECHA, @today) BETWEEN 1 AND 30 THEN 'vigente'
                    WHEN DATEDIFF(DAY,doc.CFECHA, @today) BETWEEN 31 AND 60 THEN 'vencido_60'
                    WHEN DATEDIFF(DAY,doc.CFECHA, @today) > 61 THEN 'vencido'
                END AS estatus,
                doc.CTOTAL total,
                doc.CPENDIENTE pendiente,
                (SELECT TOP 1 CSCMOVTO FROM admMovimientos WHERE CIDDOCUMENTO = 13623 AND CSCMOVTO <> '') AS segmento
            FROM admDocumentos doc
            INNER JOIN admFoliosDigitales folios ON folios.CIDDOCTO = doc.CIDDOCUMENTO
            WHERE {" AND ".join(conditions)} AND doc.CIDDOCUMENTODE = 4
            ORDER BY doc.CFECHA ASC;
        """

    def get(self, conditions=[], args=()) -> ClienteDict:
        sql = self._build_sql_cliente(conditions, top=1)
        try:
            dbname = get_dbname(self.env, "comercial")
            print(dbname)
            with self.env["ev.tools.mssql"].connect(dbname) as db:
                result = db.fetchone(sql, args)
                return self.env["ev.tools"].dict_parser(result)
        except Exception as e:
            raise ValueError(str(e))

    def search(self, **kwargs):
        conditions, params = self._build_conditions(**kwargs)
        offset, limit = get_pagination(**kwargs)
        sql = f"""
            {self._build_sql_cliente(conditions)}
            ORDER BY c.CFECHAALTA DESC
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
        """

        params.extend([offset, limit])

        try:
            dbname = get_dbname(self.env, "comercial")

            with self.env["ev.tools.mssql"].connect(dbname) as db:
                return db.fetchall(sql, tuple(params))
        except Exception as e:
            raise ValueError(str(e))

    def saldos(self, saldo_cero=True):
        """Funcion para obtener el estado de cuenta de los clientes"""

        sql_cte = f"""
            WITH EstadoDeCuenta AS (
                SELECT
                    doc.CIDCLIENTEPROVEEDOR AS id_cliente,

                    COUNT(*) AS total_facturas,

                    SUM(doc.CPENDIENTE) AS saldo_total,

                    SUM(CASE WHEN DATEDIFF(DAY, doc.CFECHA, @today) BETWEEN 1 AND 30 
                        THEN doc.CPENDIENTE ELSE 0 END) AS saldo_a_30,

                    SUM(CASE WHEN DATEDIFF(DAY, doc.CFECHA, @today) BETWEEN 31 AND 60 
                        THEN doc.CPENDIENTE ELSE 0 END) AS saldo_a_60,

                    SUM(CASE WHEN DATEDIFF(DAY, doc.CFECHA, @today) BETWEEN 61 AND 90 
                        THEN doc.CPENDIENTE ELSE 0 END) AS saldo_a_90,

                    SUM(CASE WHEN DATEDIFF(DAY, doc.CFECHA, @today) > 90 
                        THEN doc.CPENDIENTE ELSE 0 END) AS saldo_vencido

                FROM admDocumentos doc

                WHERE
                    doc.CIDDOCUMENTODE = 4
                    {"AND doc.CPENDIENTE > 0" if not saldo_cero else ""}

                GROUP BY
                    doc.CIDCLIENTEPROVEEDOR
            )
        """

        sql = f"""
            DECLARE @today DATE = CAST(GETDATE() AS DATE);

            {sql_cte}
            
            SELECT
                c.CIDCLIENTEPROVEEDOR [cliente.id],
                c.CCODIGOCLIENTE [cliente.codigo],
                c.CRAZONSOCIAL [cliente.nombre],
                c.CRFC [cliente.rfc],
                cv.CVALORCLASIFICACION [clasificacion.valor],
                cv.CCODIGOVALORCLASIFICACION [clasificacion.codigo],
            CONCAT_WS(',', c.CEMAIL1, c.CEMAIL2, c.CEMAIL3) [cliente.emails],
                edo.total_facturas,
                edo.saldo_total,
                edo.saldo_a_30,
                edo.saldo_a_60,
                edo.saldo_a_90,
                edo.saldo_vencido
            FROM admClientes c
            INNER JOIN EstadoDeCuenta edo ON edo.id_cliente = c.CIDCLIENTEPROVEEDOR
            INNER JOIN admClasificacionesValores cv ON cv.CIDVALORCLASIFICACION = c.CIDVALORCLASIFCLIENTE1
        """

        try:
            dbname = get_dbname(self.env, "comercial")
            with self.env["ev.tools.mssql"].connect(dbname) as db:
                return db.fetchall(sql)
        except Exception as e:
            raise ValueError(str(e))

    def detalle_saldos(self, **kwargs):
        try:
            dbname = get_dbname(self.env, "comercial")
            with self.env["ev.tools.mssql"].connect(dbname) as db:
                conditions, args, conditions_cliente, args_cliente = (
                    self._build_conditions_saldo(**kwargs)
                )
                cliente = self.get(conditions_cliente, tuple(args_cliente))
                sql = self._buil_sql_saldo_detalle(conditions)
                cliente["facturas"] = db.fetchall(sql, tuple(args))
                return self.env["ev.tools"].dict_parser(cliente)
        except Exception as e:
            raise ValueError(str(e))
