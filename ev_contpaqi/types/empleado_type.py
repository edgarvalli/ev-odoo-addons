from datetime import datetime
from typing import TypedDict


class EmpleadoDict(TypedDict):
    id: int
    codigo: str
    nombre: str
    rfc: str
    curp: str
    fechaalta: datetime
    numerosegurosocial: str
    codigopostal: str
    tiposalario: str
    jornada: str
    puesto: str
    departamento: str
    correo: str
    sbc: str
    cidregistropatronal: str
    guiddsl: str
    empresa: str
