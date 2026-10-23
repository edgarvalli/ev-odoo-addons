from typing import Literal
from decimal import Decimal
from dataclasses import dataclass, asdict, field

TipoImpuesto = Literal["traslado", "retencion"]
TipoFactor = Literal["Tasa", "Cuota", "Exento"]
ImpuestoSAT = Literal["01", "02", "03"]
tipo_impuestos = {
    "001": "ISR",
    "002": "IVA",
    "003": "IEPS",
}


@dataclass
class Impuesto:
    _impuesto_sat_name: str

    base: Decimal
    impuesto: str  # Clave SAT: 001 ISR, 002 IVA, 003 IEPS
    tipo_factor: TipoFactor
    tipo_impuesto: TipoImpuesto
    porcentaje: Decimal
    clave_impuesto: ImpuestoSAT = "02"
    tasa_o_cuota: Decimal | None = None

    @property
    def importe(self) -> Decimal | None:
        if self.tipo_factor == "Exento" or self.tasa_o_cuota is None:
            return None

        return self.base * self.tasa_o_cuota

    @property
    def nombre_impuesto(self) -> str:
        return tipo_impuestos.get(self.impuesto, "NO APLICA")

    def to_dict(self):
        return asdict(self)


@dataclass
class Concepto:
    clave_prod_serv: str
    cantidad: Decimal
    clave_unidad: str
    nombre_unidad: str
    descripcion: str
    valor_unitario: Decimal
    objeto_imp: str
    clave_impuesto: ImpuestoSAT = "02"
    descuento: Decimal | None = None
    impuestos: list[Impuesto] = field(default_factory=list)

    @property
    def subtotal(self) -> Decimal:
        return self.cantidad * self.valor_unitario

    @property
    def total_impuestos_trasladados(self) -> Decimal:
        return sum(
            (
                impuesto.importe or Decimal("0")
                for impuesto in self.impuestos
                if impuesto.tipo_impuesto == "traslado"
            ),
            start=Decimal("0"),
        )

    @property
    def total_impuestos_retenidos(self) -> Decimal:
        return sum(
            (
                impuesto.importe or Decimal("0")
                for impuesto in self.impuestos
                if impuesto.tipo_impuesto == "retencion"
            ),
            start=Decimal("0"),
        )

    @property
    def total(self) -> Decimal:
        descuento = self.descuento or Decimal("0")

        return (
            self.subtotal
            - descuento
            + self.total_impuestos_trasladados
            - self.total_impuestos_retenidos
        )

    def to_dict(self) -> dict:
        data = asdict(self)
        data["subtotal"] = self.subtotal
        data["total_impuestos_trasladados"] = self.total_impuestos_trasladados
        data["total_impuestos_retenidos"] = self.total_impuestos_retenidos
        data["total"] = self.total
        return data
