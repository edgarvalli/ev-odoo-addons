from pathlib import Path
from typing import Union, List, Optional
from lxml import etree
from .ev_comprobante import BaseDTO, EmisorDTO, ReceptorDTO, TimbreDTO, ComprobanteBase


# =========================
# DTOs
# =========================


class PercepcionDTO(BaseDTO):
    def __init__(self, node, ns):
        super().__init__(node, ns)
        self.tipo = node.get("TipoPercepcion")
        self.clave = node.get("Clave")
        self.concepto = node.get("Concepto")
        self.importe_gravado = node.get("ImporteGravado")
        self.importe_exento = node.get("ImporteExento")


class DeduccionDTO(BaseDTO):
    def __init__(self, node, ns):
        super().__init__(node, ns)
        self.tipo = node.get("TipoDeduccion")
        self.clave = node.get("Clave")
        self.concepto = node.get("Concepto")
        self.importe = node.get("Importe")


class OtroPagoDTO(BaseDTO):
    def __init__(self, node, ns):
        super().__init__(node, ns)
        self.tipo = node.get("TipoOtroPago")
        self.clave = node.get("Clave")
        self.concepto = node.get("Concepto")
        self.importe = node.get("Importe")

        subsidio = node.find("nomina12:SubsidioAlEmpleo", namespaces=node.nsmap)
        self.subsidio_causado = (
            subsidio.get("SubsidioCausado") if subsidio is not None else None
        )


class NominaDTO(BaseDTO):
    def __init__(self, node, ns):
        super().__init__(node, ns)
        self.tipo_nomina = node.get("TipoNomina")
        self.fecha_pago = node.get("FechaPago")
        self.fecha_inicial = node.get("FechaInicialPago")
        self.fecha_final = node.get("FechaFinalPago")
        self.dias_pagados = node.get("NumDiasPagados")

        self.total_percepciones = node.get("TotalPercepciones")
        self.total_deducciones = node.get("TotalDeducciones")

        self.percepciones: List[PercepcionDTO] = []
        self.deducciones: List[DeduccionDTO] = []
        self.otros_pagos: List[OtroPagoDTO] = []

        self._parse()

    def _parse(self):
        # Percepciones
        for p in self.findall(".//nomina12:Percepcion"):
            self.percepciones.append(PercepcionDTO(p))

        # Deducciones
        for d in self.findall(".//nomina12:Deduccion"):
            self.deducciones.append(DeduccionDTO(d))

        # Otros pagos
        for o in self.findall(".//nomina12:OtroPago"):
            self.otros_pagos.append(OtroPagoDTO(o))


# =========================
# MAIN CLASS
# =========================
class ComprobanteNominaXML(ComprobanteBase):

    def __init__(self, xml: Union[str, bytes, Path]):
        super().__init__(xml)
        self.emisor: Optional[EmisorDTO] = None
        self.receptor: Optional[ReceptorDTO] = None
        self.nomina: Optional[NominaDTO] = None
        self.timbre: Optional[TimbreDTO] = None

        self._parse()

    def _parse_xml(self, xml):
        if isinstance(xml, bytes):
            return etree.fromstring(xml)

        if isinstance(xml, Path):
            return etree.parse(str(xml)).getroot()

        if isinstance(xml, str):
            xml = xml.strip()
            if xml.startswith("<"):
                return etree.fromstring(xml.encode())

            path = Path(xml)
            return etree.parse(str(path)).getroot()

        raise TypeError("Tipo no soportado")

    def _get_namespaces(self):
        ns = self.root.nsmap.copy()
        if None in ns:
            ns["cfdi"] = ns.pop(None)
        return ns

    def _parse(self):
        self._parse_common_data()

        # Nomina
        node = self.root.find(".//nomina12:Nomina", namespaces=self.ns)
        if node is not None:
            self.nomina = NominaDTO(node, self.ns)

        # Timbre
        node = self.root.find(".//tfd:TimbreFiscalDigital", namespaces=self.ns)
        if node is not None:
            self.timbre = TimbreDTO(node)

    def to_dict(self):
        return {
            "emisor": self.emisor.to_dict() if self.emisor else None,
            "receptor": self.receptor.to_dict() if self.receptor else None,
            "nomina": self.nomina.to_dict() if self.nomina else None,
            "timbre": self.timbre.to_dict() if self.timbre else None,
        }
