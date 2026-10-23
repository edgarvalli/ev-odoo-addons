import requests
from typing import Any
from base64 import b64encode
from decimal import Decimal
from requests.auth import HTTPBasicAuth

from ..models.conceptos import Concepto
from ..interfaces.types import HttpMethod
from ..models.config import EvTimbradoConfig
from ..models.comprobante import Comprobante
from ..models.responses import AuthFacturamaResponse
from ..interfaces.facturama_responses import FacturaResponse


class FacturamaClient:

    def __init__(self, config: EvTimbradoConfig):
        self.url = (
            "https://apisandbox.facturama.mx"
            if config.mode == "dev"
            else "https://api.facturama.mx"
        )

        self.config = config
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(config.user, config.password)
        self.session.headers.update({"Content-Type": "application/json"})

    def _build_headers(self):
        auth = b64encode(f"{self.config.user}:{self.config.password}".encode()).decode()
        return {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

    def _build_taxes(self, concepto: Concepto) -> list[dict[str, Any]]:
        return[
            {
                "Total": float(impuesto.importe or Decimal("0")),
                "Name": impuesto.nombre_impuesto,
                "Base": float(impuesto.base),
                "Rate": (
                float(impuesto.tasa_o_cuota)
                if impuesto.tasa_o_cuota is not None
                else None
            ),
                "IsRetention": impuesto.tipo_impuesto == "retencion"
            } for impuesto in concepto.impuestos
        ]

    def _build_conceptos(self, comprobante: Comprobante) -> dict:
        return [
            {
                "ProductCode": c.clave_prod_serv,
                "IdentificationNumber": c.clave_prod_serv,
                "Description": c.descripcion,
                "Unit": c.nombre_unidad,
                "UnitCode": c.clave_unidad,
                "UnitPrice": c.valor_unitario,
                "Quantity": c.cantidad,
                "Subtotal": c.subtotal,
                "TaxObject": c.clave_impuesto,
                "Total": float(c.total),
                "Taxes": self._build_taxes(c)
            } for c in comprobante.conceptos
        ]
    
    def _build_factura(self, comprobante: Comprobante) -> dict:
        return {
            "NameId": "",
            "Folio": comprobante.folio,
            "CfdiType": comprobante.tipo_comprobante,
            "PaymentForm": comprobante.forma_pago,
            "PaymentMethod": comprobante.metodo_pago,
            "ExpeditionPlace": "78000",
            "Date": comprobante.fecha.strftime("%Y-%m-%dT%H:%M:%S"),
            "Receiver": {
                "Rfc": comprobante.receptor.rfc,
                "Name": comprobante.receptor.nombre,
                "CfdiUse": comprobante.receptor.uso_cfdi,
                "TaxZipCode": comprobante.receptor.domicilio_fiscal,
                "FiscalRegime": comprobante.receptor.regimen_fiscal
            },
            "Items": self._build_conceptos(comprobante)
        }

    def make_request(self, path: str, *,method: HttpMethod = "get", body: dict = None):
        url = f"{self.url.rstrip("/")}/{path.lstrip("/")}"
        method_action = getattr(self.session, method)
        if method_action:
            return method_action(url, json=body).json()

    def test(self):
        values = self.make_request("client")
        return [AuthFacturamaResponse.from_dict(val) for val in values]

    def emitir(self, comprobante: Comprobante) -> FacturaResponse:
        return self.make_request("/3/cfdis", method="post", body=self._build_factura(comprobante))

    def cancelar(self, comprobante: Comprobante):
        url = f"/cfdi/{comprobante.id}?type={comprobante.tipo_comprobante}&motive={comprobante.cancelacion.clave}&uuidReplacement={comprobante.uuid}"
        return self.make_request(url, method="delete")