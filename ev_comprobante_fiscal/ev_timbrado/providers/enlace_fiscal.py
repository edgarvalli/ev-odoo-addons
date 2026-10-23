from ..models.config import EvTimbradoConfig
from ..models.comprobante import Comprobante


class EnlaceFiscal:

    def __init__(self, config: EvTimbradoConfig):
        self.config = EvTimbradoConfig

    def emitir(self, comprobante: Comprobante):
        print(comprobante)

    def cancelar(self, comprobante: Comprobante):
        print(comprobante)

    def consultar(self, comprobante: Comprobante):
        print(comprobante)
