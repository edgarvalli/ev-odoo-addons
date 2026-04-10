from datetime import timedelta
from odoo import models, fields, api


class EVInvSoftwareLicense(models.Model):
    _name = "ev.inv.license"
    _description = "EV - Licencias"
    _rec_name = "name"
    _order = "expiration_date asc"

    name = fields.Char("Nombre")
    license_key = fields.Char("No. Licencia")
    license_type = fields.Selection(
        [
            ("perpetual", "Perpetua"),
            ("subscription", "Suscripción"),
            ("trial", "Prueba"),
            ("free", "Gratis"),
            ("oem", "OEM"),
        ],
        string="Tipo de Licencia",
        default="subscription",
    )
    software_id = fields.Many2one("ev.inv.software", "ID Software", ondelete="cascade")
    device_id = fields.Many2one("ev.inv.devices", string="Dispositivo")
    user_id = fields.Many2one("res.users", "Usuario")
    renewal_reminder_days = fields.Integer("Avisar antes", default=30)
    expiration_date = fields.Date("Fecha de Vencimiento")
    days_to_expire = fields.Integer(
        "Días para vencer",
        compute="_compute_license_status",
        store=True,
    )
    notes = fields.Text("Observaciones")

    @api.depends("expiration_date")
    def _compute_license_status(self):
        today = fields.Date.today()
        for rec in self:
            if rec.expiration_date:
                rec.days_to_expire = (rec.expiration_date - today).days
            else:
                rec.days_to_expire = 0

    @api.onchange("device_id")
    def _onchange_device(self):

        for rec in self:
            rec.user_id = self.device_id.user_id

    ############
    # ACTIONS  #
    ############

    def _get_expiring_licenses(self):
        self = self.sudo()
        today = fields.Date.today()

        max_date = today + timedelta(days=30)

        licenses = self.search(
            [
                ("expiration_date", ">=", today),
                ("expiration_date", "<=", max_date),
            ]
        )

        return licenses

    def action_notify_expiring_licenses(self):
        licenses = self._get_expiring_licenses()
        if not licenses:
            return
        admins = self.env.ref("base.group_system").user_ids
        if not admins:
            return

        template = self.env.ref("ev_it_inventory.email_template_license_expiry")

        for admin in admins:
            template.with_context(
                licenses=licenses,
                email_to=admin.email,
            ).send_mail(self.id, force_send=False)
