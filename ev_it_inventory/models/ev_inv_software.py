from odoo import models, fields, api


class EVInvSoftware(models.Model):
    _name = "ev.inv.software"
    _description = "EV - Software"
    _rec_name = "name"
    _order = "expiration_date asc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Software", required=True)
    version = fields.Char("Versión")
    vendor_id = fields.Many2one("ev.inv.vendors", "Fabricante / Proveedor")

    license_key = fields.Char("Clave de Licencia")
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

    license_ids = fields.One2many("ev.inv.license", "software_id", string="Licencias")

    seats = fields.Integer("Número de Licencias", default=1)
    used_seats = fields.Integer("Licencias en Uso", default=0)

    purchase_date = fields.Date("Fecha de Compra")
    activation_date = fields.Date("Fecha de Activación")
    expiration_date = fields.Date("Fecha de Vencimiento")

    cost = fields.Float("Costo")
    currency_id = fields.Many2one(
        "res.currency",
        string="Moneda",
        default=lambda self: self.env.company.currency_id.id,
    )

    device_id = fields.Many2one(
        "ev.inv.devices",
        string="Equipo Asignado",
    )

    user_id = fields.Many2one(
        "res.users",
        string="Usuario Asignado",
    )

    company_id = fields.Many2one(
        "res.company",
        string="Empresa",
        default=lambda self: self.env.company.id,
    )

    notes = fields.Text("Observaciones")

    is_expired = fields.Boolean(
        "Vencido",
        compute="_compute_license_status",
        store=True,
    )

    days_to_expire = fields.Integer(
        "Días para vencer",
        compute="_compute_license_status",
        store=True,
    )

    invoice_number = fields.Char("Factura")
    supplier_id = fields.Many2one("res.partner", string="Proveedor")
    renewal_reminder_days = fields.Integer("Avisar antes", default=30)

    @api.depends("expiration_date")
    def _compute_license_status(self):
        today = fields.Date.today()
        for rec in self:
            if rec.expiration_date:
                rec.days_to_expire = (rec.expiration_date - today).days
                rec.is_expired = rec.expiration_date < today
            else:
                rec.days_to_expire = 0
                rec.is_expired = False


class EVInvSoftwareLicense(models.Model):
    _name = "ev.inv.license"
    _description = "EV - Licnecias"
    _rec_name = "name"

    name = fields.Char("Nombre")
    license_key = fields.Char("No. Licencia")
    software_id = fields.Many2one("ev.inv.software", "ID Software")
    device_id = fields.Many2one("ev.inv.devices", string="Dispositivo")
    user_id = fields.Many2one("res.users", "Usuario")
    expiration_date = fields.Date("Fecha de Vencimiento")
    notes = fields.Text("Observaciones")

    @api.onchange("device_id")
    def _onchange_device(self):

        for rec in self:
            rec.user_id = self.device_id.user_id
