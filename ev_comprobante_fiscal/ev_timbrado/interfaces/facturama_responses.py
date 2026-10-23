from typing import TypedDict, NotRequired


class TaxAddress(TypedDict):
    Street: str
    ExteriorNumber: str
    InteriorNumber: NotRequired[str]
    Neighborhood: str
    ZipCode: str
    Municipality: str
    State: str
    Country: str


class IssuedIn(TypedDict):
    Street: str
    ExteriorNumber: str
    Neighborhood: str
    ZipCode: str
    Municipality: str
    State: str
    Country: str


class Issuer(TypedDict):
    FiscalRegime: str
    Rfc: str
    TaxName: str
    Email: str
    Phone: str
    TaxAddress: TaxAddress
    IssuedIn: IssuedIn


class Receiver(TypedDict):
    Rfc: str
    Name: str
    Email: NotRequired[str]


class Item(TypedDict):
    ProductCode: str
    IdentificationNumber: str
    UnitCode: str
    Discount: float
    CuentaPredial: str
    Quantity: float
    Unit: str
    Description: str
    UnitValue: float
    Total: float


class Tax(TypedDict):
    Total: float
    Name: str
    Rate: float
    Type: str


class TaxStamp(TypedDict):
    Uuid: str
    Date: str
    CfdiSign: str
    SatCertNumber: str
    SatSign: str
    RfcProvCertif: str


class Complement(TypedDict):
    TaxStamp: TaxStamp


class FacturaResponse(TypedDict):
    Id: str
    CfdiType: str
    Type: str
    Serie: str
    Folio: str
    Date: str
    CertNumber: str
    PaymentTerms: str
    PaymentConditions: str
    PaymentMethod: str
    PaymentAccountNumber: str
    PaymentBankName: str
    ExpeditionPlace: str
    ExchangeRate: float
    Currency: str
    Subtotal: float
    Discount: float
    Total: float
    Observations: str
    OrderNumber: str
    Issuer: Issuer
    Receiver: Receiver
    Items: list[Item]
    Taxes: list[Tax]
    Complement: Complement
    Status: str
    OriginalString: str
