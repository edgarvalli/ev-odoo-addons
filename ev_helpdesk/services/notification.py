import logging

from odoo.models import Model
from odoo.tools import html2plaintext

from ..utils.emails import normalize_emails

_logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, record: Model):
        self.record = record

    def _get_ticket_recipients(self) -> list[str]:
        ticket = self.record
        recipients = [
            ticket.user_id.email,
            ticket.assigned_user_id.email,
        ]
        return [email for email in recipients if email]

    def send_notification_ticket(
        self,
        template_xmlid: str,
        recipients: list[str],
        emails_cc: list[str] | None = None,
        context: dict | None = None,
    ) -> None:
        self.record.ensure_one()

        emails = normalize_emails(recipients)
        cc_emails = normalize_emails(emails_cc)

        if not emails:
            _logger.warning(
                "Notificación omitida: ticket=%s, motivo=sin destinatarios.",
                self.record.name,
            )
            return

        recipient_set = {email.casefold() for email in emails}
        cc_emails = [
            email for email in cc_emails if email.casefold() not in recipient_set
        ]

        template = self.record.env.ref(
            template_xmlid,
            raise_if_not_found=False,
        )

        if not template:
            _logger.error(
                "Plantilla de correo no encontrada: ticket=%s, plantilla=%s.",
                self.record.name,
                template_xmlid,
            )
            return

        if template.model != self.record._name:
            _logger.error(
                "Modelo incompatible en plantilla: ticket=%s, plantilla=%s, "
                "modelo_plantilla=%s.",
                self.record.name,
                template_xmlid,
                template.model,
            )
            return

        email_values = {"email_to": ",".join(emails)}

        if context:
            attachment_ids = context.get("attachment_ids", [])

            if attachment_ids:
                email_values["attachment_ids"] = [
                    (4, attachment_id) for attachment_id in attachment_ids
                ]

        if cc_emails:
            email_values["email_cc"] = ",".join(cc_emails)

        # Inyectar variables para que la plantilla pueda acceder a ellas con ctx.
        template = template.with_context(**(context or {}))

        mail_id = template.send_mail(
            self.record.id,
            force_send=False,
            email_values=email_values,
        )

        _logger.info(
            "Notificación encolada: ticket=%s, plantilla=%s, "
            "mail_id=%s, destinatarios=%s, CC=%s.",
            self.record.name,
            template_xmlid,
            mail_id,
            ", ".join(emails),
            ", ".join(cc_emails) or "(ninguno)",
        )

    def notify_ticket_created(self):
        # 1. Notificar al solicitante
        self.send_notification_ticket(
            "ev_helpdesk.mail_template_ev_helpdesk_ticket_created",
            [self.record.user_id.email],
        )

        # 2. Notificar a los administradores de Helpdesk
        admins = self.record.env["res.users"].search(
            [
                ("share", "=", False),
                ("active", "=", True),
            ]
        )

        admin_emails = [
            user.email
            for user in admins
            if user.has_group("ev_helpdesk.group_helpdesk_admin") and user.email
        ]

        if admin_emails:
            self.send_notification_ticket(
                "ev_helpdesk.mail_template_ev_helpdesk_team_ticket_created",
                admin_emails,
            )

        # 3. Notificar al equipo asignado, si existe
        team = self.record.team_id

        if not team:
            _logger.info(
                "El ticket %s no tiene equipo asignado; "
                "se omite la notificación al equipo.",
                self.record.name,
            )
            return

        team_emails = []

        manager = team.manager_id
        if manager and manager.email:
            team_emails.append(manager.email)

        for member in team.member_ids:
            if member.email:
                team_emails.append(member.email)

        if team_emails:
            self.send_notification_ticket(
                "ev_helpdesk.mail_template_ev_helpdesk_team_ticket_created",
                team_emails,
            )

    def notify_ticket_assigned(self) -> None:
        technician = self.record.assigned_user_id

        if not technician or not technician.email:
            _logger.warning(
                "No se notificó la asignación del ticket %s: "
                "el técnico no tiene correo electrónico.",
                self.record.name,
            )
            return

        self.send_notification_ticket(
            template_xmlid=("ev_helpdesk.mail_template_ev_helpdesk_ticket_assigned"),
            recipients=[technician.email],
        )

    def notify_ticket_updated(self) -> None:
        recipients = self._get_ticket_recipients()

        self.send_notification_ticket(
            template_xmlid=("ev_helpdesk.mail_template_ev_helpdesk_ticket_updated"),
            recipients=recipients,
        )

    def notify_ticket_comment(
        self, comment: str = "", attachment_ids: list[int] | None = None
    ) -> None:
        recipients = self._get_ticket_recipients()
        comment_text = html2plaintext(comment or "")

        self.send_notification_ticket(
            template_xmlid=("ev_helpdesk.mail_template_ev_helpdesk_ticket_updated"),
            recipients=recipients,
            context={
                "comment": comment_text,
                "attachment_ids": attachment_ids or [],
            },
        )
