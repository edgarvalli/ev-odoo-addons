from odoo.models import AbstractModel
from odoo.exceptions import UserError
import logging
from typing import List

_logger = logging.getLogger(__name__)


class Comercial(AbstractModel):
    _name = "ev.contpaqi.comercial"

    # -------------------------------------------
    #   Helpers
    # -------------------------------------------

    def _build_sql_cliente(self, conditions: List[str] = []):
        return f"""
            SELECT
                c.CIDCLIENTEPROVEEDOR id,
                c.CCODIGOCLIENTE codigo,
                c.CRAZONSOCIAL razon_social,
                c.CFECHAALTA fecha_alta,
                c.CFECHABAJA fecha_baja,
                c.CRFC rfc,
                c.CCURP curp,
                CONCAT_WS(',',
                    NULLIF(LTRIM(RTRIM(c.CEMAIL1)), ''),
                    NULLIF(LTRIM(RTRIM(c.CEMAIL2)), ''),
                    NULLIF(LTRIM(RTRIM(c.CEMAIL3)), '')
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
            WHERE {" AND ".join(conditions)}
        """

    def empresas(self):
        sql = """
            SELECT
                CIDEMPRESA id,
                CNOMBREEMPRESA empresa,
                CRUTADATOS ruta_datos,
                RIGHT(CRUTADATOS,CHARINDEX('\\', REVERSE(CRUTADATOS)) - 1) AS dbname
            FROM Empresas WHERE CIDEMPRESA > 1;
        """
        try:
            with self.env["ev.tools.mssql"].connect("CompacWAdmin") as db:
                return db.fetchall(sql)
        except Exception as err:
            raise UserError(str(err))
        
    def clientes(self, **kwargs):

        dbname = self.env.company.ev_contpaqi_comercial_db

        if not dbname:
            return None

        try:
            limit = int(kwargs.pop("limit", 50))
            page = int(kwargs.pop("page", 1))
        except:
            _logger.warning(
                "No se envio un dato entero en las propiedades limit o page"
            )
            return None

        offset = ((page - 1) * limit) if page > 1 else 0
        args = []
        conditions = ["c.CIDCLIENTEPROVEEDOR > 1"]

        if "q" in kwargs:
            conditions.append(
                "(c.CCODIGOCLIENTE LIKE ? OR c.CRAZONSOCIAL LIKE ? OR c.CRFC LIKE ?)"
            )
            q = kwargs["q"] + "%"
            args.append(q)
            args.append(q)
            args.append(q)

        sql = f"""
            {self._build_sql_cliente(conditions)}
            ORDER BY c.CFECHAALTA DESC
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
        """
        args.append(offset)
        args.append(limit)

        with self.env["ev.tools.mssql"].connect(dbname) as db:
            return db.fetchall(sql, tuple(args))

    def buscar_cliente(self, codigo: str):
        dbname = self.env.company.ev_contpaqi_comercial_db

        if not dbname:
            return None

        conditions = ["c.CCODIGOCLIENTE = ?"]
        sql = self._build_sql_cliente(conditions)

        mssql = self.env["ev.tools.mssql"]
        with mssql.connect(dbname) as db:
            return db.fetchone(sql, (codigo,))

    def buscar_cliente_id(self, id: int):
        dbname = self.env.company.ev_contpaqi_comercial_db

        if not dbname:
            return None

        conditions = ["c.CIDCLIENTEPROVEEDOR = ?"]
        sql = self._build_sql_cliente(conditions)

        mssql = self.env["ev.tools.mssql"]
        with mssql.connect(dbname) as db:
            return db.fetchone(sql, (id,))

    def saldo_clientes(self, saldo_cero=True):
        """Funcion para obtener el estado de cuenta de los clientes"""

        dbname = self.env.company.ev_contpaqi_comercial_db

        if not dbname:
            return None

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

        with self.env["ev.tools.mssql"].connect(dbname) as db:
            return db.fetchall(sql)

    def saldo_cliente_detalle(self, **kwargs):
        """Funcion para obtener el estado de cuenta actual del cliente"""
        dbname = self.env.company.ev_contpaqi_comercial_db

        if not dbname:
            return None
        conditions = []
        args = []
        conditions_cliente = []
        args_cliente = []

        idcliente = kwargs.get("id")
        if not idcliente:
            codigo_cliente = kwargs.get("codigo")

            if not codigo_cliente:
                _logger.info("Debe de definir id:int o codigo:str")
                return None

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

        sql = f"""
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
                folios.CUUID uuid,
                CASE
                    WHEN DATEDIFF(DAY,doc.CFECHA, @today) BETWEEN 1 AND 30 THEN 'Vigente'
                    WHEN DATEDIFF(DAY,doc.CFECHA, @today) BETWEEN 31 AND 60 THEN 'Vencido a 60 dias'
                    WHEN DATEDIFF(DAY,doc.CFECHA, @today) BETWEEN 61 AND 90 THEN 'Vencido a 90 dias'
                    WHEN DATEDIFF(DAY,doc.CFECHA, @today) > 90 THEN 'Vencido'
                END AS estatus,
                doc.CTOTAL total,
                doc.CPENDIENTE pendiente
            FROM admDocumentos doc
            INNER JOIN admFoliosDigitales folios ON folios.CIDDOCTO = doc.CIDDOCUMENTO
            WHERE {" AND ".join(conditions)} AND doc.CIDDOCUMENTODE = 4
            ORDER BY doc.CFECHA ASC;
        """
        with self.env["ev.tools.mssql"].connect(dbname) as db:
            cliente = db.fetchone(
                self._build_sql_cliente(conditions_cliente), tuple(args_cliente)
            )
            cliente["facturas"] = db.fetchall(sql, tuple(args))
            return self.env["ev.tools"].dict_parser(cliente)
