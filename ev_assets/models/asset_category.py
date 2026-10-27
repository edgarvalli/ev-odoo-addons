from odoo import fields, models


class EVAssetCategory(models.Model):
    _name = "ev.asset.category"
    _description = "EV - Categoría de activo"
    _order = "name"

    name = fields.Char(string="Nombre", required=True, translate=True)
    code = fields.Char(string="Código", required=True, index=True)
    description = fields.Text(string="Descripción")
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint(
        "UNIQUE(code)",
        "El código de categoría debe ser único.",
    )
