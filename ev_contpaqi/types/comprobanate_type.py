from typing import TypedDict, Optional, Literal, List
from datetime import datetime


class Emisor(TypedDict):
    nombre: Optional[str]
    rfc: str
    regimen: str
    regimen_desc: str
    registro_patronal: str
    regimen_fiscal: str


class Empleado(TypedDict):
    nombre: str
    rfc: str
    nss: str
    curp: str
    fecha_inicio_rel_laboral: str
    tipo_contrato: str
    tipo_contrato_desc: str
    tipo_jornada: str
    tipo_jornada_desc: str
    jornada: str
    departamento: str
    puesto: str
    codigo_postal: str
    periodicidad_pago: str
    periodicidad_pago_desc: str
    periodicidad: str
    sbc: float
    tipo_salario: str
    regimen: str
    regimen_desc: str
    regimen_fiscal: str


class TotalesPercepcion(TypedDict):
    total_exento: float
    total_gravado: float


class TotalesDeduccion(TypedDict):
    total_exento: float
    total_gravado: float


class Totales(TypedDict):
    total_sueldo: float
    total_otros_pagos: float
    total_percepciones: float
    total_deducciones: float
    total_impuestos_retenidos: float
    total_otras_deducciones: float
    subtotal: float
    neto: float
    percepcion: TotalesPercepcion
    deduccion: TotalesDeduccion


class TimbreCfdi(TypedDict):
    no_certificado_sat: str
    fecha: str
    sello: str
    sello_sat: str
    version: str
    rfc_proveedor_certificador: str
    complemento_certificacion: str


class MetadataCfdi(TypedDict):
    content: str
    metodo_pago: str
    no_certificado: str
    sello: str
    certificado: str
    version: str
    uuid: str
    timbre: TimbreCfdi


class MovimientoNomina(TypedDict):
    guid_document: str
    tipo: Literal["D", "P", "OP"]
    tipo_desc: str
    id_detalle: int
    clave_sat: str
    clave_sat_desc: str
    codigo: str
    concepto: str
    importe_gravado: float
    importe_exento: float
    importe: float


class NominaRow(TypedDict):
    id_documento: int
    id_empleado: int
    id_periodo: int
    guid_document: str
    fecha_completa: datetime
    fecha: str
    hora: str
    fecha_inicial_pago: datetime
    fecha_final_pago: datetime
    ejercicio: int
    periodo: int
    fecha_pago: datetime
    fecha_pago_mes: datetime
    ejercicio_pago: int
    dias_pagados: float
    uuid: str
    lugar_expedicion: str
    version: str
    version_complemento: str
    uso_cfdi: str
    sat_url: str

    emisor: Emisor
    empleado: Empleado
    totales: Totales

    cfdi: MetadataCfdi

    percepciones: List[MovimientoNomina]
    deducciones: List[MovimientoNomina]


class ComprobanteBase(TypedDict):
    iddocumento: int
    idperiodo: int
    fechaemision: str
    fechapago: str
    fechafinal: str
    fechainicial: str
    diaspagados: float
    uuid: str
    guiddocdsl: str
    guiddocumento: str
    sbc: float
    total: float
    nombreemisor: str
    rfcemisor: str


class Comprobante(ComprobanteBase):
    pass


class ComprobanteWithXML(ComprobanteBase):
    content: str


class ComprobantesParams(TypedDict, total=False):
    idempleado: int
    startdate: str
    enddate: str
    xml: bool
    page: int
    limit: int
