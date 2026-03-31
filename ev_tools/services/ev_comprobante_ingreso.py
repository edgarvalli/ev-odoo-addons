from pathlib import Path
from typing import Union, List, Optional
from .ev_comprobante import BaseDTO, EmisorDTO, ReceptorDTO, ComprobanteBase


# =========================
# DTOs
# =========================


class TrasladoDTO(BaseDTO):
    def __init__(self, node, ns):
        super().__init__(node, ns)
        self.base = node.get("Base")
        self.impuesto = node.get("Impuesto")
        self.tipo_factor = node.get("TipoFactor")
        self.tasa = node.get("TasaOCuota")
        self.importe = node.get("Importe")


class ConceptoDTO(BaseDTO):

    def __init__(self, node, ns):
        super().__init__(node, ns)
        self.clave_prod_serv = node.get("ClaveProdServ")
        self.cantidad = node.get("Cantidad")
        self.clave_unidad = node.get("ClaveUnidad")
        self.descripcion = node.get("Descripcion")
        self.valor_unitario = node.get("ValorUnitario")
        self.importe = node.get("Importe")

        self.traslados: List[TrasladoDTO] = []

        self._parse()

    def _parse(self):
        traslados = self.findall(".//cfdi:Traslado")
        for t in traslados:
            self.traslados.append(TrasladoDTO(t))


class ImpuestosDTO(BaseDTO):
    def __init__(self, node, ns):
        super().__init__(node, ns)
        self.total_trasladados = node.get("TotalImpuestosTrasladados")
        self.traslados: List[TrasladoDTO] = []

        for t in node.findall(".//cfdi:Traslado", namespaces=ns):
            self.traslados.append(TrasladoDTO(t))


class TimbreDTO(BaseDTO):
    def __init__(self, node, ns):
        super().__init__(node, ns)
        self.uuid = node.get("UUID")
        self.fecha_timbrado = node.get("FechaTimbrado")
        self.rfc_proveedor = node.get("RfcProvCertif")


# =========================
# MAIN
# =========================
class ComprobanteIngresoXML(ComprobanteBase):

    def __init__(self, xml: Union[str, bytes, Path]):
        super().__init__(xml)

        self.emisor: Optional[EmisorDTO] = None
        self.receptor: Optional[ReceptorDTO] = None
        self.conceptos: List[ConceptoDTO] = []
        self.impuestos: Optional[ImpuestosDTO] = None
        self.timbre: Optional[TimbreDTO] = None

        self._parse()

    def _parse(self):
        self._parse_common_data()

        # Conceptos
        for c in self.findall(".//cfdi:Concepto"):
            self.conceptos.append(ConceptoDTO(c, self.ns))

        # Impuestos globales
        node = self.find("cfdi:Impuestos")
        if node is not None:
            self.impuestos = ImpuestosDTO(node, self.ns)

        # Timbre
        node = self.find(".//tfd:TimbreFiscalDigital")
        if node is not None:
            self.timbre = TimbreDTO(node)

    def to_dict(self):
        return {
            "emisor": self.emisor.to_dict() if self.emisor else None,
            "receptor": self.receptor.to_dict() if self.receptor else None,
            "conceptos": [c.to_dict() for c in self.conceptos],
            "impuestos": self.impuestos.to_dict() if self.impuestos else None,
            "timbre": self.timbre.to_dict() if self.timbre else None,
        }
