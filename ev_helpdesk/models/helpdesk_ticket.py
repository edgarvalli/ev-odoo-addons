from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from ..services.notification import NotificationService


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

    is_admin = fields.Boolean(compute="_compute_user_permissions")
    is_team_member = fields.Boolean(compute="_compute_user_permissions")

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

        tickets = super().create(vals_list)
        for ticket in tickets:
            NotificationService(ticket).notify_ticket_created()

        return tickets

    def write(self, vals):
        vals = vals.copy()
        now = fields.Datetime.now()

        # Guardar valores anteriores para detectar cambios reales.
        tracked_fields = (
            "stage_id",
            "priority",
            "subject",
            "description",
            "resolution",
            "team_id",
            "category_id",
            "asset_id",
        )

        previous_values = {
            record.id: {
                field_name: (
                    record[field_name].id
                    if record._fields[field_name].type == "many2one"
                    else record[field_name]
                )
                for field_name in tracked_fields
            }
            for record in self
        }

        previous_assignees = {}
        if "assigned_user_id" in vals:
            for record in self:
                new_assignee_id = vals["assigned_user_id"] or False
                if record.assigned_user_id.id != new_assignee_id:
                    previous_assignees[record.id] = True

            if vals["assigned_user_id"]:
                vals.setdefault("date_assigned", now)
            else:
                vals["date_assigned"] = False

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

        result = super().write(vals)

        for record in self:
            notification = NotificationService(record)

            # Notificar al técnico cuando se le asigna o cambia la asignación.
            if previous_assignees.get(record.id) and record.assigned_user_id:
                notification.notify_ticket_assigned()

            # Notificar cambios relevantes, como etapa o prioridad.
            changed_fields = [
                field_name
                for field_name in tracked_fields
                if previous_values[record.id][field_name]
                != (
                    record[field_name].id
                    if record._fields[field_name].type == "many2one"
                    else record[field_name]
                )
            ]

            if changed_fields:
                notification.notify_ticket_updated()

        return result

    def message_post(self, **kwargs):
        message_type = kwargs.get("message_type", "comment")
        comment = kwargs.get("body", "")

        notify_comment = message_type == "comment" and not self.env.context.get(
            "skip_ticket_comment_notification"
        )

        message = super().message_post(**kwargs)

        if notify_comment:
            for ticket in self:
                NotificationService(ticket).notify_ticket_comment(
                    comment=comment,
                    attachment_ids=message.attachment_ids.ids,
                )

        return message

    def action_assign_to_me(self):
        """Asigna el ticket al usuario actual."""
        for record in self:
            record.write({"assigned_user_id": self.env.user.id})

    def action_set_in_progress(self):
        """Mueve el ticket a la etapa En progreso."""
        stage = self.env["ev.helpdesk.stage"].search(
            [("name", "=", "En progreso"), ("active", "=", True)],
            limit=1,
        )
        if not stage:
            raise ValidationError(_("No existe la etapa 'En progreso'."))

        self.write({"stage_id": stage.id})

    def action_close(self):
        """Cierra el ticket usando una etapa final."""
        stage = self.env["ev.helpdesk.stage"].search(
            [("is_closed", "=", True), ("active", "=", True)],
            order="sequence, id",
            limit=1,
        )

        if not stage:
            raise ValidationError(_("No hay una etapa final configurada."))

        self.write({"stage_id": stage.id})

    def _compute_user_permissions(self):
        user = self.env.user

        is_admin = user.has_group("ev_helpdesk.group_helpdesk_admin")

        is_team_member = bool(
            self.env["ev.helpdesk.team"].search_count(
                [
                    ("member_ids", "=", user.id),
                ]
            )
        )

        for record in self:
            record.is_admin = is_admin
            record.is_team_member = is_team_member
