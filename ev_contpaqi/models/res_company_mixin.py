from odoo import models, fields, api
from odoo.exceptions import UserError


class ResCompanyMixin(models.Model):
    _inherit = "res.company"

    ev_contpaqi_nominas_db = fields.Selection(
        string="Empresa Contpaqi Nominas",
        selection="_empresas_nominas_contpaqi",
        store=True,
    )

    ev_contpaqi_comercial_db = fields.Selection(
        string="Empresa Contpaqi Comercial",
        selection="_empresas_comercial_contpaqi",
        store=True,
    )

    @api.model
    def _empresas_comercial_contpaqi(self):
        """Obtiene las empresas de comercial"""
        comercial = self.env["ev.contpaqi.comercial"]

        try:
            empresas = comercial.empresas()
            if not empresas:
                raise UserError("No se encontraron empresas")
            return [(e["dbname"], e["empresa"]) for e in empresas]
        except Exception as e:
            raise UserError(e)

    @api.model
    def _empresas_nominas_contpaqi(self):
        """Obtiene dinámicamente la lista de empresas de Nominas Contpaqi"""
        nominas = self.env["ev.contpaqi.nominas"]
        try:
            empresas = nominas.empresas(fields="NombreEmpresa name, RutaEmpresa dbname")
            if not empresas:
                raise UserError("No se encontraron empresas")

            # Devuelve lista de tuplas para Selection
            return [(e["dbname"], e["name"]) for e in empresas]
        except Exception as err:
            raise UserError(str(err))
