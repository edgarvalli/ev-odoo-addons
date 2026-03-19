from typing import Dict
from types import SimpleNamespace
import xml.etree.ElementTree as ET
from odoo.models import AbstractModel
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from ..tools.sqltools import empleado_query

import logging

_logger = logging.getLogger(__name__)


class Nominas(AbstractModel):
    _name = "ev.contpaqi.nominas"

    ### Metodos

    def empresas(self, fields: str = "*"):
        try:
            with self.env["ev.tools.mssql"].connect("nomGenerales") as db:
                sql = f"SELECT {fields} FROM NOM10000 WHERE IDEmpresa <> 1;"
                return db.fetchall(sql)
        except Exception as err:
            raise UserError(str(err))

    def obtener_dsl(self):
        dbname = self.env.company.ev_contpaqi_nominas_db.dbname
        try:
            with self.env["ev.tools.mssql"].connect(dbname) as db:

                row = db.fetchone(f"SELECT GUIDDSL FROM [{dbname}].dbo.NOM10000")
                if not row:
                    raise UserError("No se encontro DSL.")

                dsl = row["GUIDDSL"]
                return dsl
        except Exception as err:
            raise UserError(str(err))

    def empleados(self, **kwargs):
        dbname = self.env.company.ev_contpaqi_nominas_db.dbname or None

        if not dbname:
            raise UserError("No se ha configurado la base de datos en la compañia.")

        with self.env["ev.tools.mssql"].connect(dbname) as db:
            sql, args = empleado_query(dbname, kwargs=kwargs)
            return db.fetchall(sql, args)

    def buscar_empleado(self, codigo: str):
        dbname = self.env.company.ev_contpaqi_nominas_db.dbname or None

        if not dbname:
            raise UserError("No se ha configurado la base de datos en la compañia.")

        try:
            with self.env["ev.tools.mssql"].connect(dbname) as db:
                sql, args = empleado_query(dbname, {"codigoempleado": codigo})
                return db.fetchone(sql, args)
        except Exception as err:
            raise UserError(str(err))

    def buscar_empleado_id(self, id: int):
        dbname = self.env.company.ev_contpaqi_nominas_db.dbname or None

        if not dbname:
            raise UserError("No se ha configurado la base de datos en la compañia.")

        try:
            with self.env["ev.tools.mssql"].connect(dbname) as db:
                sql, args = empleado_query(dbname, {"empleadoid": id})
                return db.fetchone(sql, args)
        except Exception as err:
            raise UserError(str(err))

    def comprobantes(self, **kwargs):

        try:
            limit = int(kwargs.pop("limit", 50))
            page = int(kwargs.pop("page", 1))
        except:
            _logger.warning(
                "No se envio un dato entero en las propiedades limit o page"
            )
            return None

        offset = ((page - 1) * limit) if page > 1 else 0
        idempleado = kwargs.pop("idempleado")
        included_xml = kwargs.pop("xml", False)

        dbname = self.env.company.ev_contpaqi_nominas_db.dbname

        try:
            with self.env["ev.tools.mssql"].connect(dbname) as db:

                dsl = self._get_dsl(db)

                conditions = ["IdEmpleado = ?", "comprobante.GUIDDocumentoDSL <> ''"]

                args = [idempleado]

                startdate = kwargs.get("startdate")
                enddate = kwargs.get("enddate")

                if startdate:
                    enddate = enddate or datetime.now().strftime("%Y-%m-%d")

                    end_dt = datetime.strptime(enddate, "%Y-%m-%d") + timedelta(days=1)

                    conditions.append("FechaEmision >= ?")
                    conditions.append("FechaEmision < ?")

                    args.append(startdate)
                    args.append(end_dt.strftime("%Y-%m-%d"))

                query = f"""
                    SELECT 
                        iddocumento,
                        idperiodo,
                        FORMAT(FechaEmision,'yyyy-MM-dd HH:mm:ss') fechaemision,
                        FORMAT(FechaPago,'yyyy-MM-dd HH:mm:ss') fechapago,
                        FORMAT(FechaFinalPago,'yyyy-MM-dd HH:mm:ss') fechafinal,
                        FORMAT(FechaInicialPago,'yyyy-MM-dd HH:mm:ss') fechainicial,
                        NumDiasPagados diaspagados,
                        comprobante.UUID uuid,
                        GUIDDocumentoDSL guiddocdsl,
                        GUIDDocumento guiddocumento,
                        sbc,
                        c.Total total,
                        c.NombreEmisor nombreemisor,
                        c.RFCEmisor rfcemisor
                        {",dc.Content content" if included_xml else ""}
                    FROM [{dbname}].dbo.NOM10043 comprobante
                    {
                        "INNER JOIN [document_{dsl}_content].dbo.DocumentContent dc ON dc.GuidDocument = comprobante.GUIDDocumentoDSL"
                        if included_xml else ""
                    }                    
                    INNER JOIN [document_{dsl}_metadata].dbo.Comprobante c
                        ON c.GuidDocument = comprobante.GUIDDocumentoDSL
                    WHERE {" AND ".join(conditions)}
                    ORDER BY FechaEmision DESC
                    OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
                """

                args.append(offset)
                args.append(limit)

                return db.fetchall(query, tuple(args))

        except Exception as err:
            raise UserError(str(err))

    def verificar_pertenencia_comprobante(self, codigo: str, iddocumento: int) -> bool:
        if not codigo or not iddocumento:
            return False

        dbname = self.env.company.ev_contpaqi_nominas_db.dbname or None

        if not dbname:
            raise UserError("No se ha configurado la base de datos en la compañia.")

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

        try:

            with self.env["ev.tools.mssql"].connect(dbname) as db:
                result = db.fetchone(sql, (iddocumento, codigo.strip()))
                return result is not None
        except Exception:
            return False

    def datos_comprobante(self, id_documento: int):
        dbname = self.env.company.ev_contpaqi_nominas_db.dbname

        try:
            with self.env["ev.tools.mssql"].connect(dbname) as db:

                dsl = self._get_dsl(db)

                comprobante = self._get_nomina(db, dsl, id_documento)
                detalle = self._get_nomina_detalle(db, dsl, comprobante.guid_document)
                comprobante.cfdi = self._get_timbrado(
                    db, dsl, comprobante.guid_document
                )

                comprobante.percepciones = detalle.percepciones
                comprobante.deducciones = detalle.deducciones

                total = f"{comprobante.totales.neto:.6f}"
                sello = comprobante.cfdi.timbre.sello[-8:]

                comprobante.sat_url = (
                    "https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx"
                    f"?id={comprobante.uuid}"
                    f"&re={comprobante.emisor.rfc}"
                    f"&rr={comprobante.empleado.rfc}"
                    f"&tt={total}"
                    f"&fe={sello}"
                )

                return comprobante

        except Exception as err:
            raise UserError(f"Error obteniendo comprobante: {err}")

    ##### HELPERS ###########

    def _get_dsl(self, db):
        dbname = self.env.company.ev_contpaqi_nominas_db.dbname
        try:
            row = db.fetchone(f"SELECT GUIDDSL FROM [{dbname}].dbo.NOM10000")
            if not row:
                raise UserError("No se encontro DSL.")

            dsl = row["GUIDDSL"]
            return dsl
        except Exception as err:
            raise UserError(str(err))

    def _get_nomina(self, db, dsl: str, id_documento: int):

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

        _doc: Dict = db.fetchone(sql, (id_documento,))

        if not _doc:
            raise UserError("No se encontro datos del documento.")

        return evtools.dict_to_namespace(_doc)

    def _get_nomina_detalle(self, db, dsl: str, guid_document: str):
        evtools = self.env["ev.tools"]

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

        percepciones = []
        deducciones = []

        moves = db.fetchall(sql, (guid_document,))

        for item in moves:

            obj = evtools.dict_to_namespace(item)
            if obj.tipo == "D":
                deducciones.append(obj)
            else:
                percepciones.append(obj)

        return SimpleNamespace(percepciones=percepciones, deducciones=deducciones)

    def _get_timbrado(self, db, dsl: str, guid_document: str) -> SimpleNamespace:
        evtools = self.env["ev.tools"]
        sql = f"""
            SELECT
                DocumentType type,
                filename,
                content
            FROM [document_{dsl}_content].[dbo].[DocumentContent]
            WHERE GuidDocument = ?
        """

        result = db.fetchone(sql, (guid_document,))

        if not result:
            raise UserError("No se encontro el XML")

        cfdi = evtools.dict_to_namespace(result)

        namespaces = {
            "cfdi": "http://www.sat.gob.mx/cfd/4",
            "nomina12": "http://www.sat.gob.mx/nomina12",
            "tfd": "http://www.sat.gob.mx/TimbreFiscalDigital",
        }

        xml_content = cfdi.content

        if isinstance(xml_content, bytes):
            xml_content = xml_content.decode("utf-8")

        comprobante = ET.fromstring(xml_content)

        metodo_map = {
            "PUE": "PUE - Pago en una sola exhibición",
            "PPD": "PPD - Pago en parcialidades o diferido",
        }

        cfdi.metodo_pago = metodo_map.get(comprobante.get("MetodoPago"), "")

        timbrado = comprobante.find(".//tfd:TimbreFiscalDigital", namespaces)

        if timbrado is None:
            raise UserError("El XML no contiene Timbre Fiscal Digital")

        cfdi.no_certificado = comprobante.get("NoCertificado")
        cfdi.sello = comprobante.get("Sello", "")
        cfdi.certificado = comprobante.get("Certificado", "")
        cfdi.version = comprobante.get("Version", "")
        cfdi.uuid = timbrado.get("UUID", "")

        cfdi.timbre = SimpleNamespace()

        cfdi.timbre.no_certificado_sat = timbrado.get("NoCertificadoSAT", "")
        cfdi.timbre.fecha = timbrado.get("FechaTimbrado", "")
        cfdi.timbre.sello = timbrado.get("SelloCFD", "")
        cfdi.timbre.sello_sat = timbrado.get("SelloSAT", "")
        cfdi.timbre.version = timbrado.get("Version", "1.1")
        cfdi.timbre.rfc_proveedor_certificador = timbrado.get("RfcProvCertif", "")

        cfdi.timbre.complemento_certificacion = (
            "||"
            + "|".join(
                [
                    cfdi.timbre.version,
                    cfdi.uuid,
                    cfdi.timbre.fecha,
                    cfdi.timbre.rfc_proveedor_certificador,
                    cfdi.timbre.sello,
                    cfdi.timbre.no_certificado_sat,
                ]
            )
            + "||"
        )

        return cfdi
