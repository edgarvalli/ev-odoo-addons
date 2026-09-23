from typing import Optional, Union
from datetime import datetime, timedelta
from .comprobantes_tool import ComprobanteTools
from ...tools.contpaqi_tools import get_dsl
from .tools import get_pagination, empleado_query
from .types import Comprobante, ComprobanteWithXML, ComprobantesParams


class NominasComprobante(ComprobanteTools):

    def _build_sql(
        self,
        db,
        dbname: str,
        conditions: Optional[list[str]] = None,
        included_xml=False,
        top: int = None,
    ) -> str:

        conditions = conditions or []
        dsl = get_dsl(db, dbname, "nominas")

        where_clause = ""
        xml_clause = ""

        if included_xml:
            xml_clause = (
                f"INNER JOIN [document_{dsl}_content].dbo.DocumentContent dc "
                f"ON dc.GuidDocument = comprobante.GUIDDocumentoDSL"
            )

        if conditions:
            where_clause = f"WHERE {' AND '.join(conditions)}"

        fields = [
            "iddocumento",
            "idperiodo",
            "FORMAT(FechaEmision,'yyyy-MM-dd HH:mm:ss') fechaemision",
            "FORMAT(FechaPago,'yyyy-MM-dd HH:mm:ss') fechapago",
            "FORMAT(FechaFinalPago,'yyyy-MM-dd HH:mm:ss') fechafinal",
            "FORMAT(FechaInicialPago,'yyyy-MM-dd HH:mm:ss') fechainicial",
            "NumDiasPagados diaspagados",
            "comprobante.UUID uuid",
            "GUIDDocumentoDSL guiddocdsl",
            "GUIDDocumento guiddocumento",
            "sbc",
            "c.Total total",
            "c.NombreEmisor nombreemisor",
            "c.RFCEmisor rfcemisor",
        ]

        if included_xml:
            fields.append("dc.Content content")

        sql = f"""
            SELECT {f'TOP {top}' if top else ''}
                {','.join(fields)}
            FROM [{dbname}].dbo.NOM10043 comprobante
            {xml_clause}                    
            INNER JOIN [document_{dsl}_metadata].dbo.Comprobante c
                ON c.GuidDocument = comprobante.GUIDDocumentoDSL
            {where_clause}
            ORDER BY FechaEmision DESC
        """
        return sql

    def get(self, iddocumento: int) -> Union[Comprobante, ComprobanteWithXML]:

        try:
            conditions = ["comprobante.IdDocumento = ?"]
            args = (iddocumento,)

            with self.env["ev.tools.mssql"].connect(self.dbname) as db:
                sql = self._build_sql(
                    db, dbname=self.dbname, top=1, conditions=conditions
                )
                return db.fetchone(sql, args)

        except Exception as e:
            raise ValueError(str(e))

    def search(
        self, **kwargs: ComprobantesParams
    ) -> Union[list[Comprobante], list[ComprobanteWithXML]]:

        page, limit = get_pagination(**kwargs)
        offset = ((page - 1) * limit) if page > 1 else 0
        idempleado = kwargs.get("idempleado")
        included_xml = kwargs.get("xml", False)

        if not idempleado:
            raise ValueError("idempleado es requerido")

        try:

            conditions = [
                "comprobante.IdEmpleado = ?",
                "comprobante.GUIDDocumentoDSL <> ''",
            ]

            args = [idempleado]

            startdate = kwargs.get("startdate")
            enddate = kwargs.get("enddate")

            if startdate:
                enddate = enddate or datetime.now().strftime("%Y-%m-%d")

                try:
                    end_dt = datetime.strptime(enddate, "%Y-%m-%d") + timedelta(days=1)
                except ValueError:
                    raise ValueError("Formato de fecha inválido (YYYY-MM-DD)")

                conditions.append("FechaEmision >= ?")
                conditions.append("FechaEmision < ?")

                args.append(startdate)
                args.append(end_dt.strftime("%Y-%m-%d"))

            args.append(offset)
            args.append(limit)

            with self.env["ev.tools.mssql"].connect(self.dbname) as db:
                base_sql = self._build_sql(db, self.dbname, conditions, included_xml)
                sql = base_sql + " OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
                return db.fetchall(sql, tuple(args))

        except Exception as err:
            raise ValueError(str(err))
