from lxml import etree
from xml.etree.cElementTree import Element
from pathlib import Path
from typing import Union, Optional, List, Dict


class ComprobanteBase:

    def __init__(self, xml: Union[str, bytes, Path]):
        self.root = self._parse_xml(xml)
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

    def _parse_common_data(self):
        # Emisor
        node = self.find("cfdi:Emisor")
        if node is not None:
            self.emisor = EmisorDTO(node)

        # Receptor
        node = self.find("cfdi:Receptor")
        if node is not None:
            self.receptor = ReceptorDTO(node)

    def find(self, xpath: str) -> Element:
        return self.root.find(xpath, namespaces=self.ns)

    def findall(self, xpath: str) -> List[Element]:
        return self.root.findall(xpath, namespaces=self.ns)


# =========================
# DTO BASE
# =========================
class BaseDTO:

    def __init__(self, node: Element, ns: Optional[Dict] = None):
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
        self.uuid = node.get("UUID")
        self.fecha_timbrado = node.get("FechaTimbrado")
        self.rfc_proveedor = node.get("RfcProvCertif")
