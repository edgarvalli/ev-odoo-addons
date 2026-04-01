from decimal import Decimal
from datetime import datetime
from typing import TypedDict, Optional, Literal


class DeparmentDict(TypedDict):
    iddepartamento: int
    descripcion: str


class EmpleadoDict(TypedDict):
    idempleado: int
    idpuesto: int
    iddepartamento: int
    codigoempleado: str
    nombre: str
    fechanacimiento: Optional[datetime]
    fechaalta: Optional[datetime]
    fechabaja: Optional[datetime]
    nss: str
    email: Optional[str]
    sexo: Literal["male", "female", "other"]
    estadocivil: Optional[str]
    sueldodiario: Decimal
    sueldointegrado: Decimal
    sueldobaseliquidacion: Decimal


class JobDict(TypedDict):
    idpuesto: int
    numeropuesto: str
    descripcion: str
