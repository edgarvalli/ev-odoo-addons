from uuid import UUID
from datetime import datetime
from dataclasses import dataclass

from ..utils.dates import parse_iso_date


@dataclass
class TimbreFiscal:
    version: str
    uuid: UUID
    fecha_timbrado: datetime
    no_certificado_sat: str
    sello_cfd: str
    sello_sat: str

    def __post_init__(self):
        if isinstance(self.uuid, str):
            self.uuid = UUID(self.uuid)

        if isinstance(self.fecha, str):
            self.fecha = parse_iso_date(self.fecha)
