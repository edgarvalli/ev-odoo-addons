from odoo import fields, models


class EVAssetModel(models.Model):
    _name = "ev.asset.model"
    _description = "EV - Modelo de activo"
    _order = "brand_id, name"

    name = fields.Char(string="Modelo", required=True)
    brand_id = fields.Many2one(
        comodel_name="ev.asset.brand",
        string="Marca",
        required=True,
        ondelete="restrict",
        index=True,
    )
    description = fields.Text(string="Descripción")
    active = fields.Boolean(default=True)

    _brand_model_unique = models.Constraint(
        "UNIQUE(brand_id, name)",
        "Este modelo ya existe para la marca seleccionada.",
    )
