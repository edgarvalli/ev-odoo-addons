# from .comprobante import Comprobante

# comprobante = {
#     "version": "4.0",
#     "tipo_comprobante": "I",
#     "serie": "A",
#     "folio": "1001",
#     "fecha_emision": "2026-10-21 11:00:00",
#     "uuid": None,
#     "subtotal": 1000.00,
#     "descuentos": 0.00,
#     "total": 1160.00,
#     "tipo_moneda": "MXN",
#     "exportacion": "01",
#     "metodo_pago": "PUE",
#     "forma_pago": "03",
#     "condiciones_pago": None,
#     "tipo_cambio": 1.00,
#     "emisor": {
#         "rfc": "AAA010101AAA",
#         "nombre": "EMPRESA EMISORA SA DE CV",
#         "regimen_fiscal": "601",
#         "lugar_expedicion": "64000",
#     },
#     "receptor": {
#         "rfc": "XAXX010101000",
#         "nombre": "PUBLICO EN GENERAL",
#         "regimen_fiscal": "616",
#         "domicilio_fiscal": "64000",
#         "uso_cfdi": "S01",
#     },
#     "conceptos": [
#         {
#             "clave_prod_serv": "81112100",
#             "cantidad": 1.0,
#             "clave_unidad": "E48",
#             "descripcion": "Servicio de consultoría informática",
#             "valor_unitario": 1000.00,
#             "importe": 1000.00,
#             "descuento": None,
#             "objeto_imp": "02",
#             "impuestos": [
#                 {
#                     "base": 1000.00,
#                     "impuesto": "002",
#                     "tipo_factor": "Tasa",
#                     "tasa_o_cuota": 0.160000,
#                     "importe": 160.00,
#                 }
#             ],
#         }
#     ],
# }

# c = Comprobante(**comprobante)

from ..ev_timbrado import EVTimbrado
from ..ev_timbrado.models.config import EvTimbradoConfig
from ..ev_timbrado.models.comprobante import Comprobante

c = Comprobante()

print(c)
