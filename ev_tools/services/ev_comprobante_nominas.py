from pathlib import Path
from xml.etree.cElementTree import Element
from typing import Union, List, Optional
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
            self.percepciones.append(PercepcionDTO(p, self.ns))

        # Deducciones
        for d in self.findall(".//nomina12:Deduccion"):
            self.deducciones.append(DeduccionDTO(d, self.ns))

        # Otros pagos
        for o in self.findall(".//nomina12:OtroPago"):
            self.otros_pagos.append(OtroPagoDTO(o, self.ns))


class PersonNominaBase:
    def __init__(self, tag: str, root: Element):
        ns = {"cfdi": "http://www.sat.gob.mx/cfd/4"}
        node = root.find(tag, namespaces=ns)
        self.rfc = node.get("Rfc", "")
        self.nombre = node.get("Nombre", "")
        if "Receptor" in tag:
            self.regimen_fiscal = node.get("RegimenFiscalReceptor", "")
        else:
            self.regimen_fiscal = node.get("RegimenFiscal", "")

    def to_dict(self):
        return self.__dict__


class ReceptorNomina(PersonNominaBase):
    def __init__(self, root: Element):
        super().__init__(".//cfdi:Receptor", root)
        ns = {
            "cfdi": "http://www.sat.gob.mx/cfd/4",
            "nomina12": "http://www.sat.gob.mx/nomina12",
        }

        node = root.find(".//cfdi:Receptor", namespaces=ns)
        self.domicilio_fiscal = node.get("DomicilioFiscalReceptor", "")
        self.uso_cfdi = node.get("UsoCFDI", "")

        node = root.find(".//nomina12:Receptor", namespaces=ns)

        self.curp = node.get("Curp", "")
        self.nss = node.get("NumSeguridadSocial", "")
        self.fecha_inicio_rel_laboral = node.get("FechaInicioRelLaboral", "")
        self.antiguedad = node.get("Antigüedad", "")
        self.tipo_contrato = node.get("TipoContrato", "")
        self.sindicalizado = node.get("Sindicalizado", "no")
        self.tipo_jornada = node.get("TipoJornada", "")
        self.tipo_regimen = node.get("TipoRegimen", "")
        self.numero_empleado = node.get("NumEmpleado", "")
        self.departamento = node.get("Departamento", "")
        self.puesto = node.get("Puesto", "")
        self.riesgo_puesto = node.get("RiesgoPuesto", "")
        self.periocidad_pago = node.get("PeriodicidadPago", "")
        self.sbc = float(node.get("SalarioBaseCotApor", 0))
        self.salario_diario_integrado = float(node.get("SalarioDiarioIntegrado", 0))
        self.clave_entidad_fed = node.get("ClaveEntFed", "NLE")


class EmisorNomina(PersonNominaBase):
    def __init__(self, root: Element):

        super().__init__(".//cfdi:Emisor", root)
        ns = {"nomina12": "http://www.sat.gob.mx/nomina12"}
        node = root.find(".//nomina12:Emisor", namespaces=ns)
        self.registro_patronal = node.get("RegistroPatronal", "")
        ## Ultimos 6 meses javi


# =========================
# MAIN CLASS
# =========================
class ComprobanteNominaXML(ComprobanteBase):

    def __init__(self, xml: Union[str, bytes, Path]):
        super().__init__(xml)

        self.ns["tfd"] = "http://www.sat.gob.mx/TimbreFiscalDigital"

        self.emisor: Optional[EmisorDTO] = None
        self.receptor: Optional[ReceptorNomina] = None
        self.nomina: Optional[NominaDTO] = None
        self.timbre: Optional[TimbreDTO] = None
        self._parse()

    def _parse(self):
        self.emisor = EmisorNomina(self.root)
        self.receptor = ReceptorNomina(self.root)
        self._get_comprobante()

        # Nomina
        node = self.find(".//nomina12:Nomina")
        if node is not None:
            self.nomina = NominaDTO(node, self.ns)

        # Timbre
        node = self.find(".//tfd:TimbreFiscalDigital")
        if node is not None:
            self.timbre = TimbreDTO(node, self.ns)

    def to_dict(self):
        base = super().to_dict()
        return {
            **base,
            "emisor": self.emisor.to_dict() if self.emisor else None,
            "receptor": self.receptor.to_dict() if self.receptor else None,
            "nomina": self.nomina.to_dict() if self.nomina else None,
            "timbre": self.timbre.to_dict() if self.timbre else None,
        }
