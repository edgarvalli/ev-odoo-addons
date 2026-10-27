from odoo import fields, models


class EVAssetLocation(models.Model):
    _name = "ev.asset.location"
    _description = "EV - Ubicación de activo"
    _order = "name"

    name = fields.Char(string="Nombre", required=True)
    parent_id = fields.Many2one(
        comodel_name="ev.asset.location",
        string="Ubicación superior",
        ondelete="restrict",
    )
    child_ids = fields.One2many(
        comodel_name="ev.asset.location",
        inverse_name="parent_id",
        string="Ubicaciones dependientes",
    )
    description = fields.Text(string="Descripción")
    active = fields.Boolean(default=True)
