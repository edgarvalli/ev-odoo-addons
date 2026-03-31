from odoo import models, fields


class ResCompanyMixin(models.Model):
    _inherit = "res.company"

    ev_contpaqi_nominas_db = fields.Many2one(
        "ev.contpaqi.empresas",
        domain=[("system_origin", "=", "nominas")],
        string="Empresa Contpaqi Nominas",
    )
    ev_contpaqi_comercial_db = fields.Many2one(
        "ev.contpaqi.empresas",
        domain=[("system_origin", "=", "comercial")],
        string="Empresa Contpaqi Nominas",
    )

    def sync_empresas(self):
        self.env["ev.contpaqi.empresas"].action_sync()
