from typing import Literal
from dataclasses import dataclass

from .facturama import FacturamaConfig

@dataclass
class EvTimbradoConfig:
    facturama: FacturamaConfig | None = None
    mode: Literal["dev", "prod"] = "dev"
    supplier: Literal["facturama", "enlace_fiscal"] = "facturama"
