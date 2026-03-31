from typing import List, Tuple, Union, Optional
from dataclasses import dataclass
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from odoo.orm.environments import Environment
from ..tools.sqltools import get_pagination
from ..tools.contpaqi_tools import get_dsl, get_dbname
from ..types.comprobanate_type import (
    NominaRow,
    MetadataCfdi,
    MovimientoNomina,
    Comprobante,
    ComprobanteWithXML,
    ComprobantesParams,
)

# Lorena Hernandez Jimenez


@dataclass
class ComprobanteTools:
    env: Environment

    def _get_nomina(self, db, dsl: str, id_documento: int) -> NominaRow:

        evtools = self.env["ev.tools"]

        _fields_doc = [
            "doc.IdDocumento id_documento",
            "doc.IdEmpleado id_empleado",
            "doc.IdPeriodo id_periodo",
            "nomina.GuidDocument guid_document",
            "c.Fecha fecha_completa",
            "CONVERT(VARCHAR(10), c.Fecha, 103) fecha",
            "CONVERT(VARCHAR(8), c.Fecha, 108) hora",
            "nomina.FechaInicialPago fecha_inicial_pago",
            "nomina.FechaFinalPago fecha_final_pago",
            "periodo.ejercicio ejercicio",
            "periodo.numeroperiodo periodo",
            "nomina.FechaPago fecha_pago",
            "nomina.FechaPagoMes fecha_pago_mes",
            "nomina.FechaPagoAnio ejercicio_pago",
            "nomina.NumDiasPagados dias_pagados",
            "c.UUID uuid",
            "c.LugarExpDesc lugar_expedicion",
            "c.Version version",
            "nomina.Version version_complemento",
            "c.UsoCFDI uso_cfdi",
        ]

        _fields_emisor = [
            "c.NombreEmisor [emisor.nombre]",
            "c.RFCEmisor [emisor.rfc]",
            "c.RegimenEmisor [emisor.regimen]",
            "c.RegimenEmisorDesc [emisor.regimen_desc]",
            "nomina.RegistroPatronal [emisor.registro_patronal]",
            "CONCAT(c.RegimenEmisor, ' ', c.RegimenEmisorDesc) [emisor.regimen_fiscal]",
        ]

        _fields_empleado = [
            "c.NombreReceptor [empleado.nombre]",
            "c.RFCReceptor [empleado.rfc]",
            "nomina.NumSeguridadSocialRec [empleado.nss]",
            "nomina.CURPReceptor [empleado.curp]",
            "nomina.FechaInicioRelLaboral [empleado.fecha_inicio_rel_laboral]",
            "nomina.TipoContrato [empleado.tipo_contrato]",
            "nomina.TipoContratoDesc [empleado.tipo_contrato_desc]",
            "nomina.TipoJornada [empleado.tipo_jornada]",
            "nomina.TipoJornadaDesc [empleado.tipo_jornada_desc]",
            "CONCAT(nomina.TipoJornada, ' ', nomina.TipoJornadaDesc) [empleado.jornada]",
            "nomina.DepartamentoRec [empleado.departamento]",
            "nomina.PuestoRec [empleado.puesto]",
            "c.DomicilioReceptor [empleado.codigo_postal]",
            "nomina.PeriodicidadPago [empleado.periodicidad_pago]",
            "nomina.PeriodicidadPagoDesc [empleado.periodicidad_pago_desc]",
            "CONCAT(nomina.PeriodicidadPago, ' ', nomina.PeriodicidadPagoDesc) [empleado.periodicidad]",
            "nomina.SalarioBaseCotApor [empleado.sbc]",
            """
            CASE
                WHEN e.basecotizacionimss = 'F' THEN 'Fijo'
                WHEN e.basecotizacionimss = 'V' THEN 'Variable'
                WHEN e.basecotizacionimss = 'M' THEN 'Mixto'
            END AS [empleado.tipo_salario]
            """,
            "c.RegimenReceptor [empleado.regimen]",
            "c.RegimenReceptorDesc [empleado.regimen_desc]",
            "CONCAT(c.RegimenReceptor, ' ', c.RegimenReceptorDesc) AS [empleado.regimen_fiscal]",
        ]

        _fields_totales = [
            "nomina.TotalSueldos [totales.total_sueldo]",
            "nomina.TotalOtrosPagos [totales.total_otros_pagos]",
            "nomina.TotalPercepciones [totales.total_percepciones]",
            "nomina.TotalDeducciones [totales.total_deducciones]",
            "nomina.TotalImpuestosRetenidos [totales.total_impuestos_retenidos]",
            "nomina.TotalOtrasDeducciones [totales.total_otras_deducciones]",
            "(nomina.TotalSueldos + nomina.TotalOtrosPagos) [totales.subtotal]",
            "((nomina.TotalSueldos + nomina.TotalOtrosPagos) - nomina.TotalDeducciones) [totales.neto]",
            "nomina.TotalExentoPercepcion [totales.percepcion.total_exento]",
            "nomina.TotalGravadoPercepcion [totales.percepcion.total_gravado]",
            "nomina.TotalExentoDeduccion [totales.deduccion.total_exento]",
            "nomina.TotalGravadoDeduccion [totales.deduccion.total_gravado]",
        ]

        sql = f"""
        SELECT
            {",".join(_fields_doc)},
            {",".join(_fields_emisor)},
            {",".join(_fields_empleado)},
            {",".join(_fields_totales)}
        FROM  nom10043 doc
            INNER JOIN [document_{dsl}_metadata].dbo.Nomina nomina ON nomina.GuidDocument = doc.GUIDDocumentoDSL
            INNER JOIN  [document_{dsl}_metadata].dbo.Comprobante c ON c.GuidDocument = doc.GUIDDocumentoDSL
            INNER JOIN nom10002 periodo ON periodo.idperiodo = doc.IdPeriodo
            INNER JOIN nom10001 e ON e.idempleado = doc.IdEmpleado
        WHERE doc.IdDocumento = ?
        """

        _doc = db.fetchone(sql, (id_documento,))

        if not _doc:
            raise ValueError("No se encontro datos del documento.")

        return evtools.dict_parser(_doc)

    def _get_nomina_detalle(
        self, db, dsl: str, guid_document: str
    ) -> Tuple[List[MovimientoNomina], List[MovimientoNomina]]:

        sql = f"""
            SELECT
                GuidDocument guid_document,

                CASE
                    WHEN TipoNominaDetalle = 'DED' THEN 'D'
                    WHEN TipoNominaDetalle = 'PER' THEN 'P'
                    WHEN TipoNominaDetalle = 'OTR' THEN 'OP'
                END AS tipo,

                TipoNominaDetalle tipo_desc,
                IdDetalle id_detalle,

                TipoDetalle clave_sat,
                TipoDetalleDesc clave_sat_desc,

                Clave codigo,
                Concepto concepto,

                ImporteGravado importe_gravado,
                ImporteExento importe_exento,
                Importe importe

            FROM [document_{dsl}_metadata].dbo.Nomina_Detalle 
            WHERE GuidDocument=?
        """

        percepciones: List[MovimientoNomina] = []
        deducciones: List[MovimientoNomina] = []

        moves: List[MovimientoNomina] = db.fetchall(sql, (guid_document,))

        for item in moves:

            if item.get("tipo") == "D":
                deducciones.append(item)
            else:
                percepciones.append(item)

        return percepciones, deducciones

    def _get_timbrado(self, db, dsl: str, guid_document: str) -> MetadataCfdi:
        sql = f"""
            SELECT
                DocumentType type,
                filename,
                content
            FROM [document_{dsl}_content].[dbo].[DocumentContent]
            WHERE GuidDocument = ?
        """

        cfdi: MetadataCfdi = db.fetchone(sql, (guid_document,))

        if not cfdi:
            raise ValueError("No se encontro el XML")

        # cfdi = evtools.dict_to_namespace(result)

        namespaces = {
            "cfdi": "http://www.sat.gob.mx/cfd/4",
            "nomina12": "http://www.sat.gob.mx/nomina12",
            "tfd": "http://www.sat.gob.mx/TimbreFiscalDigital",
        }

        xml_content = cfdi.get("content", "")

        if not xml_content:
            raise ValueError("El XML está vacío")

        if isinstance(xml_content, bytes):
            xml_content = xml_content.decode("utf-8")

        comprobante = ET.fromstring(xml_content)

        metodo_map = {
            "PUE": "PUE - Pago en una sola exhibición",
            "PPD": "PPD - Pago en parcialidades o diferido",
        }

        cfdi["metodo_pago"] = metodo_map.get(comprobante.get("MetodoPago"), "")

        timbrado = comprobante.find(".//tfd:TimbreFiscalDigital", namespaces)

        if timbrado is None:
            raise ValueError("El XML no contiene Timbre Fiscal Digital")

        cfdi["no_certificado"] = comprobante.get("NoCertificado")
        cfdi["sello"] = comprobante.get("Sello", "")
        cfdi["certificado"] = comprobante.get("Certificado", "")
        cfdi["version"] = comprobante.get("Version", "")
        cfdi["uuid"] = timbrado.get("UUID", "")

        timbre = cfdi.setdefault("timbre", {})

        timbre["no_certificado_sat"] = timbrado.get("NoCertificadoSAT", "")
        timbre["fecha"] = timbrado.get("FechaTimbrado", "")
        timbre["sello"] = timbrado.get("SelloCFD", "")
        timbre["sello_sat"] = timbrado.get("SelloSAT", "")
        timbre["version"] = timbrado.get("Version", "1.1")
        timbre["rfc_proveedor_certificador"] = timbrado.get("RfcProvCertif", "")

        timbre["complemento_certificacion"] = (
            "||"
            + "|".join(
                [
                    timbre["version"],
                    cfdi["uuid"],
                    timbre["fecha"],
                    timbre["rfc_proveedor_certificador"],
                    timbre["sello"],
                    timbre["no_certificado_sat"],
                ]
            )
            + "||"
        )

        return cfdi

    def get_data_comprobante(self, id_documento: int):
        try:
            dbname = get_dbname(self.env, "nominas")
            with self.env["ev.tools.mssql"].connect(dbname) as db:

                dsl = get_dsl(self.env, dbname, "nominas")
                comprobante = self._get_nomina(db, dsl, id_documento)
                guid_document = comprobante.get("guid_document")
                percepciones, deducciones = self._get_nomina_detalle(
                    db, dsl, guid_document
                )

                metadata = self._get_timbrado(db, dsl, guid_document)

                comprobante["cfdi"] = metadata
                comprobante["deducciones"] = deducciones
                comprobante["percepciones"] = percepciones

                totales = comprobante.get("totales", {})
                timbre = comprobante.get("cfdi", {}).get("timbre", {})
                total = f"{totales.get('neto', 0):.6f}"
                sello = (timbre.get("sello") or "")[-8:]

                comprobante["sat_url"] = (
                    "https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx"
                    f"?id={comprobante.get('uuid')}"
                    f"&re={comprobante.get('emisor', {}).get('rfc', '')}"
                    f"&rr={comprobante.get('empleado', {}).get('rfc', '')}"
                    f"&tt={total}"
                    f"&fe={sello}"
                )

                return comprobante

        except Exception as err:
            raise ValueError(f"Error obteniendo comprobante: {err}") from err


class ComprobanteNominaService(ComprobanteTools):

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

    def get_comprobante(
        self, iddocumento: int
    ) -> Union[Comprobante, ComprobanteWithXML]:

        try:

            dbname = get_dbname(self.env, "nominas")
            conditions = ["comprobante.IdDocumento = ?"]
            args = (iddocumento,)

            with self.env["ev.tools.mssql"].connect(dbname) as db:
                sql = self._build_sql(db, dbname=dbname, top=1, conditions=conditions)
                return db.fetchone(sql, args)

        except Exception as e:
            raise ValueError(str(e))

    def comprobantes(
        self, **kwargs: ComprobantesParams
    ) -> Union[List[Comprobante], List[ComprobanteWithXML]]:

        page, limit = get_pagination(**kwargs)
        offset = ((page - 1) * limit) if page > 1 else 0
        idempleado = kwargs.get("idempleado")
        included_xml = kwargs.get("xml", False)

        if not idempleado:
            raise ValueError("idempleado es requerido")

        try:
            dbname = get_dbname(self.env, "nominas")

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

            with self.env["ev.tools.mssql"].connect(dbname) as db:
                base_sql = self._build_sql(db, dbname, conditions, included_xml)
                sql = base_sql + " OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
                return db.fetchall(sql, tuple(args))

        except Exception as err:
            raise ValueError(str(err))
