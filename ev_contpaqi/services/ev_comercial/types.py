from datetime import datetime
from typing import List, TypedDict, Literal


class FacturaDict(TypedDict):
    id_documento: int
    serie: str
    folio: int
    serie_folio: str
    fecha: datetime
    fecha_vencimiento: datetime
    observaciones: str
    referencia: str
    uuid: str
    estatus: Literal["vigente", "vencido_60", "vencido_90", "vencido"]
    total: float
    pendiente: float


class MonedaDict(TypedDict):
    id: int
    nombre: str
    simbolo: str


class CalsificacionDict(TypedDict):
    valor: str
    codigo: str


class ClienteDict(TypedDict):
    id: int
    codigo: str
    razon_social: str
    fecha_alta: datetime
    fecha_baja: datetime
    emails: str
    moneda: MonedaDict
    clasificacion: CalsificacionDict
    facturas: List[FacturaDict]
