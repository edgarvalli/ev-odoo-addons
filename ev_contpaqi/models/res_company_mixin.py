from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ResCompanyMixin(models.Model):
    _inherit = "res.company"

    ev_contpaqi_nominas_db = fields.Selection(
        string="Empresa Contpaqi Nominas", selection="_empresas_nominas_contpaqi"
    )

    ev_contpaqi_comercial_db = fields.Selection(
        string="Empresa Contpaqi Comercial", selection="_empresas_comercial_contpaqi"
    )

    @api.model
    def _empresas_comercial_contpaqi(self):
        comercial = self.env["ev.contpaqi.comercial"]

        try:
            empresas = comercial.empresas()
            if not empresas:
                return []

            return [(e["dbname"], e["empresa"]) for e in empresas]

        except Exception as e:
            _logger.error("Error obteniendo empresas comercial: %s", e)
            return []

    @api.model
    def _empresas_nominas_contpaqi(self):
        nominas = self.env["ev.contpaqi.nominas"]

        try:
            empresas = nominas.empresas(fields="NombreEmpresa name, RutaEmpresa dbname")
            if not empresas:
                return []

            return [(e["dbname"], e["name"]) for e in empresas]

        except Exception as err:
            _logger.error("Error obteniendo empresas nominas: %s", err)
            return []
