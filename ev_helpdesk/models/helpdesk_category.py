from odoo import fields, models


class EVHelpdeskCategory(models.Model):
    _name = "ev.helpdesk.category"
    _description = "EV - Categoría de soporte"
    _order = "name"

    name = fields.Char(
        string="Nombre",
        required=True,
        translate=True,
    )
    description = fields.Text(string="Descripción")
    active = fields.Boolean(default=True)

    _name_unique = models.Constraint(
        "UNIQUE(name)", "Ya existe una categoría con ese nombre."
    )
