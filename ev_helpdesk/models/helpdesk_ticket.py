from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EVHelpdeskTicket(models.Model):
    _name = "ev.helpdesk.ticket"
    _description = "EV - Ticket de soporte"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
    ]
    _order = "priority desc, create_date desc"

    # Identificación
    name = fields.Char(
        string="Folio",
        required=True,
        readonly=True,
        copy=False,
        default="/",
        index=True,
        tracking=True,
    )
    subject = fields.Char(string="Asunto", required=True, tracking=True)
    description = fields.Html(string="Descripción", required=True)

    # Solicitante y atención
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Solicitante",
        required=True,
        default=lambda self: self.env.user,
        index=True,
        tracking=True,
        ondelete="restrict",
    )
    assigned_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Técnico asignado",
        index=True,
        tracking=True,
        ondelete="restrict",
    )
    team_id = fields.Many2one(
        comodel_name="ev.helpdesk.team",
        string="Equipo de soporte",
        tracking=True,
        ondelete="restrict",
    )

    # Clasificación
    category_id = fields.Many2one(
        comodel_name="ev.helpdesk.category",
        string="Categoría",
        tracking=True,
        ondelete="restrict",
    )
    asset_id = fields.Many2one(
        comodel_name="ev.asset",
        string="Activo afectado",
        tracking=True,
        ondelete="set null",
    )
    priority = fields.Selection(
        selection=[
            ("0", "Baja"),
            ("1", "Normal"),
            ("2", "Alta"),
            ("3", "Urgente"),
        ],
        string="Prioridad",
        default="1",
        required=True,
        index=True,
        tracking=True,
    )

    # Flujo de trabajo
    stage_id = fields.Many2one(
        comodel_name="ev.helpdesk.stage",
        string="Etapa",
        required=True,
        index=True,
        tracking=True,
        ondelete="restrict",
        default=lambda self: self._default_stage_id(),
    )
    is_closed = fields.Boolean(
        string="Cerrado",
        related="stage_id.is_closed",
        store=True,
        index=True,
    )

    # Fechas de seguimiento
    date_open = fields.Datetime(
        string="Fecha de solicitud",
        default=fields.Datetime.now,
        readonly=True,
        copy=False,
    )
    date_assigned = fields.Datetime(
        string="Fecha de asignación",
        readonly=True,
        copy=False,
    )
    date_resolved = fields.Datetime(
        string="Fecha de resolución",
        readonly=True,
        copy=False,
    )

    resolution = fields.Html(string="Solución aplicada", tracking=True)
    active = fields.Boolean(string="Activo", default=True)

    @api.model
    def _default_stage_id(self):
        stage = self.env["ev.helpdesk.stage"].search(
            [("active", "=", True)],
            order="sequence, id",
            limit=1,
        )
        return stage.id

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env["ir.sequence"]

        for vals in vals_list:
            if not vals.get("name") or vals["name"] == "/":
                vals["name"] = sequence.next_by_code("ev.helpdesk.ticket") or _("Nuevo")

            if vals.get("assigned_user_id") and not vals.get("date_assigned"):
                vals["date_assigned"] = fields.Datetime.now()

            stage_id = vals.get("stage_id")
            if stage_id:
                stage = self.env["ev.helpdesk.stage"].browse(stage_id)
                if stage.is_closed and not vals.get("date_resolved"):
                    vals["date_resolved"] = fields.Datetime.now()

        return super().create(vals_list)

    def write(self, vals):
        now = fields.Datetime.now()

        if vals.get("assigned_user_id"):
            vals.setdefault("date_assigned", now)

        if "stage_id" in vals:
            stage = self.env["ev.helpdesk.stage"].browse(vals["stage_id"])

            if stage.is_closed:
                if not any(record.resolution for record in self) and not vals.get(
                    "resolution"
                ):
                    raise ValidationError(
                        _(
                            "Debes registrar la solución antes "
                            "de cerrar o resolver el ticket."
                        )
                    )

                vals.setdefault("date_resolved", now)
            else:
                vals["date_resolved"] = False

        return super().write(vals)

    def action_assign_to_me(self):
        """Asigna el ticket al usuario actual."""
        for record in self:
            record.write(
                {
                    "assigned_user_id": self.env.user.id,
                }
            )

    def action_set_in_progress(self):
        """Mueve el ticket a la etapa En progreso."""
        stage = self.env["ev.helpdesk.stage"].search(
            [
                ("name", "=", "En progreso"),
                ("active", "=", True),
            ],
            limit=1,
        )
        if not stage:
            raise ValidationError(_("No existe la etapa 'En progreso'."))

        self.write({"stage_id": stage.id})

    def action_close(self):
        """Cierra el ticket usando una etapa final."""
        stage = self.env["ev.helpdesk.stage"].search(
            [
                ("is_closed", "=", True),
                ("active", "=", True),
            ],
            order="sequence, id",
            limit=1,
        )
        if not stage:
            raise ValidationError(_("No hay una etapa final configurada."))

        self.write({"stage_id": stage.id})
