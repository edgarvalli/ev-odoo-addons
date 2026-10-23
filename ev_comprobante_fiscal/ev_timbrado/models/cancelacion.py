from typing import Literal
from dataclasses import dataclass

from ..constants.motivos_cancelacion import MOTIVOS_CANCELACION


@dataclass
class Cancelacion:
    clave: Literal["01", "02", "03", "04"]

    @property
    def motivo(self):
        return MOTIVOS_CANCELACION.get(self.clave, "Clave no existe")
