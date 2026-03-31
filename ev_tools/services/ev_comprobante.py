from lxml import etree
from pathlib import Path
from xml.etree.cElementTree import Element
from typing import Union, Optional, List, Dict
from xml.etree.cElementTree import Element


class ComprobanteBase:

    def __init__(self, xml: Union[str, bytes, Path]):
        self.root: Element = self._parse_xml(xml)
        self.ns = self._get_namespaces()

        self.emisor: Optional[EmisorDTO] = None
        self.receptor: Optional[ReceptorDTO] = None

    def _parse_xml(self, xml):
        if isinstance(xml, bytes):
            return etree.fromstring(xml)

        if isinstance(xml, Path):
            return etree.parse(str(xml)).getroot()

        if isinstance(xml, str):
            xml = xml.strip()
            if xml.startswith("<"):
                return etree.fromstring(xml.encode())

            return etree.parse(str(Path(xml))).getroot()

        raise TypeError("Tipo no soportado")

    def _get_namespaces(self):
        ns = self.root.nsmap.copy()
        if None in ns:
            ns["cfdi"] = ns.pop(None)
        return ns

    def _get_comprobante(self):
        self.fecha = self.root.get("Fecha", "")
        self.sello = self.root.get("Sello", "")
        self.nocertificado = self.root.get("NoCertificado", "")
        self.certificado = self.root.get("Certificado", "")
        self.moneda = self.root.get("Moneda", "")
        self.tipo_comprobante = self.root.get("TipoDeComprobante", "I")
        self.exportacion = self.root.get("Exportacion", "")
        self.metodo_pago = self.root.get("MetodoPago", "PUE")
        self.serie = self.root.get("Serie", "")
        self.folio = self.root.get("Folio", "")
        self.lugar_expedicion = self.root.get("LugarExpedicion", "")
        self.subtotal = float(self.root.get("SubTotal", 0))
        self.descuento = float(self.root.get("Descuento", 0))
        self.total = float(self.root.get("Total", 0))
        self.version = self.root.get("Version", "")

    def _parse(self):
        # Emisor
        node = self.find("cfdi:Emisor")
        if node is not None:
            self.emisor = EmisorDTO(node, self.ns)

        # Receptor
        node = self.find("cfdi:Receptor")
        if node is not None:
            self.receptor = ReceptorDTO(node, self.ns)

    def find(self, xpath: str) -> Element:
        return self.root.find(xpath, namespaces=self.ns)

    def findall(self, xpath: str) -> List[Element]:
        return self.root.findall(xpath, namespaces=self.ns)

    def to_dict(self) -> Dict:
        return {
            "fecha": self.fecha,
            "sello": self.sello,
            "nocertificado": self.nocertificado,
            "certificado": self.certificado,
            "moneda": self.moneda,
            "tipo_comprobante": self.tipo_comprobante,
            "exportacion": self.exportacion,
            "metodo_pago": self.metodo_pago,
            "serie": self.serie,
            "folio": self.folio,
            "lugar_expedicion": self.lugar_expedicion,
            "subtotal": self.subtotal,
            "descuento": self.descuento,
            "total": self.total,
            "version": self.version,
        }


# =========================
# DTO BASE
# =========================
class BaseDTO:

    def __init__(self, node: Element, ns: Optional[Dict]):
        self.node = node
        self.ns = ns

    def to_dict(self):
        return {
            k: (
                v.to_dict()
                if hasattr(v, "to_dict")
                else [i.to_dict() for i in v] if isinstance(v, List) else v
            )
            for k, v in self.__dict__.items()
            if k not in ["ns", "node"]
        }

    def find(self, xpath: str) -> Element:
        return self.node.find(xpath, namespaces=self.ns)

    def findall(self, xpath: str) -> List[Element]:
        return self.node.findall(xpath, namespaces=self.ns)


# =========================
# DTOs
# =========================
class EmisorDTO(BaseDTO):
    def __init__(self, node, ns):
        super().__init__(node, ns)
        self.rfc = node.get("Rfc")
        self.nombre = node.get("Nombre")
        self.regimen = node.get("RegimenFiscal")


class ReceptorDTO(BaseDTO):
    def __init__(self, node, ns):
        super().__init__(node, ns)
        self.rfc = node.get("Rfc")
        self.nombre = node.get("Nombre")
        self.uso_cfdi = node.get("UsoCFDI")


class TimbreDTO(BaseDTO):
    def __init__(self, node, ns):
        super().__init__(node, ns)
        self.version = node.get("Version", "")
        self.uuid = node.get("UUID")
        self.rfc_provedor_certificador = node.get("RfcProvCertif", "")
        self.sello_cfd = node.get("SelloCFD", "")
        self.nocertificado_sat = node.get("NoCertificadoSAT", "")
        self.fecha_timbrado = node.get("FechaTimbrado")
        self.rfc_proveedor = node.get("RfcProvCertif")
        self.sello_sat = node.get("SelloSAT", "")
