from odoo import models
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, Literal, Union
from ..services import ComprobanteIngresoXML, ComprobanteNominaXML


class EVTools(models.AbstractModel):
    _name = "ev.tools"
    _description = "Modulo con funciones comunes"

    def dict_to_namespace(self, data: Dict) -> SimpleNamespace:

        root = self.dict_parser(data)

        def convert(obj):
            if isinstance(obj, dict):
                return SimpleNamespace(**{k: convert(v) for k, v in obj.items()})
            return obj

        return convert(root)

    def dict_parser(self, data: Dict):
        root = {}

        for key, value in data.items():

            parts = key.split(".")
            cursor = root

            for part in parts[:-1]:
                cursor = cursor.setdefault(part, {})

            cursor[parts[-1]] = value

        return root

    def parse_xml_to_comprobante(
        self, xml: Union[str, bytes, Path], type: Literal["ingreso", "nomina"]
    ):

        if type == "ingreso":
            return ComprobanteIngresoXML(xml=xml)
        elif type == "nomina":
            return ComprobanteNominaXML(xml=xml)
        else:
            raise ValueError(
                "Debe de definir un tipo de comprobante ('ingreso','nomina')"
            )
