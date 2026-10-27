from odoo import fields, models


class EVHelpdeskTeam(models.Model):
    _name = "ev.helpdesk.team"
    _description = "EV - Equipo de soporte"
    _order = "name"

    name = fields.Char(
        string="Nombre del equipo",
        required=True,
    )
    manager_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsable",
        ondelete="set null",
    )
    member_ids = fields.Many2many(
        comodel_name="res.users",
        relation="ev_helpdesk_team_user_rel",
        column1="team_id",
        column2="user_id",
        string="Técnicos",
    )
    description = fields.Text(string="Descripción")
    active = fields.Boolean(default=True)

    _name_unique = models.Constraint(
        "UNIQUE(name)", "Ya existe un equipo con ese nombre."
    )
