from dataclasses import dataclass


@dataclass
class AuthFacturamaResponse:
    id: str
    rfc: str
    name: str
    fiscal_regimen: str
    uso_cfdi: str
    tax_residence: str
    numreg_id_trib: str

    @classmethod
    def from_dict(cls, values: dict) -> "AuthFacturamaResponse":
        return cls(
            id=values.get("Id", ""),
            rfc=values.get("Rfc", ""),
            name=values.get("Name", ""),
            fiscal_regimen=values.get("FiscalRegime", ""),
            uso_cfdi=values.get("CfdiUse", ""),
            tax_residence=values.get("TaxResidence", ""),
            numreg_id_trib=values.get("NumRegIdTrib", ""),
        )
