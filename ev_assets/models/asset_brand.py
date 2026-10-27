from odoo import fields, models


class EVAssetBrand(models.Model):
    _name = "ev.asset.brand"
    _description = "EV - Marca de activo"
    _order = "name"

    name = fields.Char(string="Nombre", required=True, translate=True)
    active = fields.Boolean(default=True)

    _name_unique = models.Constraint("UNIQUE(name)", "La marca ya está registrada.")
