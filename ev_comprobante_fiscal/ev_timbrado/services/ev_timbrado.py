from ..providers.facturama import FacturamaClient
from ..providers.enlace_fiscal import EnlaceFiscal
from ..models.comprobante import Comprobante
from ..models.config import EvTimbradoConfig


class EVTimbrado:
    def __init__(self, config: EvTimbradoConfig):
        self.config = config
        self.provider = self.get_provider(config)

        if not self.provider:
            raise ValueError(f"No existe el provider {config.supplier}")

    @staticmethod
    def get_provider(config: EvTimbradoConfig):
        if config.supplier == "facturama":
            return FacturamaClient(config)
        elif config.supplier == "enlace_fiscal":
            return EnlaceFiscal(config)

    def emitir(self, comprobante: Comprobante):
        return self.provider.emitir(comprobante)

    def cancelar(self, comprobante: Comprobante):
        return self.provider.cancelar(comprobante)

    def test(self):
        return self.provider.test()
