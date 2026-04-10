from odoo import models, fields, api


class EVInvSoftware(models.Model):
    _name = "ev.inv.software"
    _description = "EV - Software"
    _rec_name = "name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Software", required=True)
    version = fields.Char("Versión")
    vendor_id = fields.Many2one("ev.inv.vendors", "Fabricante / Proveedor")

    license_ids = fields.One2many("ev.inv.license", "software_id", string="Licencias")

    seats = fields.Integer("Número de Licencias", compute="_count_license", store=True)
    used_seats = fields.Integer(
        "Licencias en Uso", compute="_count_license", store=True
    )

    cost = fields.Float("Costo")
    currency_id = fields.Many2one(
        "res.currency",
        string="Moneda",
        default=lambda self: self.env.company.currency_id.id,
    )

    company_id = fields.Many2one(
        "res.company",
        string="Empresa",
        default=lambda self: self.env.company.id,
    )

    notes = fields.Text("Observaciones")

    invoice_number = fields.Char("Factura")
    supplier_id = fields.Many2one("res.partner", string="Proveedor")

    @api.depends("license_ids")
    def _count_license(self):
        for rec in self:
            rec.seats = len(rec.license_ids)
            rec.used_seats = len([l for l in rec.license_ids if l.user_id])
