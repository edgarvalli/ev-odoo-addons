from typing import Literal
from dataclasses import dataclass, asdict

from ..constants.uso_cfdi import USOS_CFDI

UsoCfdi = Literal[
    "G01",
    "G02",
    "G03",
    "I01",
    "I02",
    "I03",
    "I04",
    "I05",
    "I06",
    "I07",
    "I08",
    "D01",
    "D02",
    "D03",
    "D04",
    "D05",
    "D06",
    "D07",
    "D08",
    "D09",
    "D10",
    "S01",
    "CP01",
    "CN01",
]


@dataclass
class EmisorReceptorBase:
    rfc: str
    nombre: str
    regimen_fiscal: str

    def to_dict(self):
        return asdict(self)


@dataclass
class Emisor(EmisorReceptorBase):
    lugar_expedicion: str


@dataclass
class Receptor(EmisorReceptorBase):
    domicilio_fiscal: str
    uso_cfdi: UsoCfdi

    def __post_init__(self):
        if self.uso_cfdi not in USOS_CFDI:
            raise ValueError(f"Uso de CFDI inválido: {self.uso_cfdi}")
