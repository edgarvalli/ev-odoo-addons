from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EVAsset(models.Model):
    _name = "ev.asset"
    _description = "EV - Activo"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(string="Nombre", required=True, tracking=True)
    asset_tag = fields.Char(
        string="Número de inventario",
        required=True,
        copy=False,
        index=True,
        tracking=True,
    )
    serial_number = fields.Char(
        string="Número de serie",
        copy=False,
        index=True,
        tracking=True,
    )

    category_id = fields.Many2one(
        comodel_name="ev.asset.category",
        string="Categoría",
        required=True,
        tracking=True,
        ondelete="restrict",
    )
    brand_id = fields.Many2one(
        comodel_name="ev.asset.brand",
        string="Marca",
        tracking=True,
        ondelete="restrict",
    )
    model_id = fields.Many2one(
        comodel_name="ev.asset.model",
        string="Modelo",
        tracking=True,
        ondelete="restrict",
        domain="[('brand_id', '=', brand_id)]",
    )

    assigned_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsable",
        tracking=True,
        ondelete="set null",
    )
    location_id = fields.Many2one(
        comodel_name="ev.asset.location",
        string="Ubicación",
        tracking=True,
        ondelete="set null",
    )

    purchase_date = fields.Date(
        string="Fecha de compra",
    )
    warranty_end = fields.Date(
        string="Fin de garantía",
    )

    state = fields.Selection(
        selection=[
            ("available", "Disponible"),
            ("assigned", "Asignado"),
            ("maintenance", "En mantenimiento"),
            ("retired", "Baja"),
        ],
        string="Estado",
        required=True,
        default="available",
        tracking=True,
        index=True,
    )

    notes = fields.Html(
        string="Observaciones",
    )
    active = fields.Boolean(
        string="Activo",
        default=True,
        tracking=True,
    )

    _asset_tag_unique = models.Constraint(
        "UNIQUE(asset_tag)",
        "El número de inventario debe ser único.",
    )

    _serial_number_unique = models.Constraint(
        "UNIQUE(serial_number)",
        "El número de serie debe ser único.",
    )

    @api.constrains("assigned_user_id", "state")
    def _check_assignment(self):
        for record in self:
            if record.state == "assigned" and not record.assigned_user_id:
                raise ValidationError(
                    _("Un activo asignado debe tener " "un responsable.")
                )

    @api.constrains("brand_id", "model_id")
    def _check_brand_model(self):
        for record in self:
            if record.model_id and record.brand_id != record.model_id.brand_id:
                raise ValidationError(
                    _(
                        "La marca del activo debe coincidir "
                        "con la marca de su modelo."
                    )
                )
