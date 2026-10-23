from typing import Literal
from dataclasses import dataclass


@dataclass
class EvTimbradoConfig:
    user: str
    password: str
    mode: Literal["dev", "prod"] = "dev"
    supplier: Literal["facturama", "enlace_fiscal"] = "facturama"
