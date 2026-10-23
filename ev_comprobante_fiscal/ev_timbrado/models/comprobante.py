from uuid import UUID
from typing import Literal
from decimal import Decimal
from datetime import datetime
from dataclasses import dataclass, asdict, field

from .conceptos import Concepto
from .cancelacion import Cancelacion
from .timbre_fiscal import TimbreFiscal
from .emisor_receptor import Emisor, Receptor

from ..constants.comprobantes import TIPOS_COMPROBANTE
from ..utils.dates import parse_iso_date


@dataclass
class Comprobante:
    # Campos obligatorios del modelo interno
    fecha: datetime = datetime.now()
    emisor: Emisor | None = None
    receptor: Receptor | None = None
    conceptos: list[Concepto] = field(default_factory=list)

    # Datos del CFDI
    id: str = ""
    version: Literal["4.0"] = "4.0"
    tipo_comprobante: Literal["I", "E", "T", "N", "P"] = "I"
    serie: str | None = None
    folio: str | None = None
    uuid: UUID | None = None

    tipo_moneda: str = "MXN"
    tipo_cambio: Decimal | None = None
    exportacion: str = "01"
    metodo_pago: Literal["PUE", "PPD"] | None = "PUE"
    forma_pago: str | None = None
    condiciones_pago: str | None = None

    subtotal: Decimal = Decimal("0")
    descuentos: Decimal = Decimal("0")
    total: Decimal = Decimal("0")

    cancelacion: Cancelacion | None = None
    timbre_fiscal: TimbreFiscal | None = None

    @property
    def tipo_comprobante_text(self):
        return TIPOS_COMPROBANTE.get(self.tipo_comprobante, "Desconocido")

    def __post_init__(self):
        if isinstance(self.uuid, str):
            self.uuid = UUID(self.uuid)

        if isinstance(self.fecha, str):
            self.fecha = parse_iso_date(self.fecha)

    def to_dict(self):
        return asdict(self)
