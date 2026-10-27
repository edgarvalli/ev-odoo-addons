from odoo import fields, models


class EVHelpdeskStage(models.Model):
    _name = "ev.helpdesk.stage"
    _description = "EV - Etapa de ticket"
    _order = "sequence, id"

    name = fields.Char(
        string="Nombre",
        required=True,
        translate=True,
    )
    sequence = fields.Integer(
        string="Secuencia",
        default=10,
    )
    is_closed = fields.Boolean(
        string="Etapa de cierre",
        help="Indica que el ticket está resuelto o cerrado.",
    )
    is_folded = fields.Boolean(
        string="Plegar en kanban",
        help="Oculta las tarjetas de esta etapa en la vista kanban.",
    )
    active = fields.Boolean(default=True)
    description = fields.Text(string="Descripción")
