from odoo import models
from types import SimpleNamespace
from typing import Dict
from pathlib import Path
from odoo.modules.module import get_module_path


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

    def module_path(self, module_name: str) -> Path:
        module_path = get_module_path(module_name)
        return Path(module_path)
