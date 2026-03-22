import re, logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class EVComprobante(models.Model):
    _name = "ev.comprobante.fiscal"
    _description = "[EV] Comprobante Fiscal"
    _rec_name = "uuid"
    _sql_constraints = [("unique_uuid", "unique(uuid)", "El UUID ya existe.")]

    tipo = fields.Selection(
        selection=lambda self: self._tipo_comprobante(),
        string="Tipo de Comprobante",
        required=True,
    )

    uuid = fields.Char("UUID", index=True, copy=False, readonly=True)

    metodo_pago_id = fields.Many2one(
        comodel_name="ev.catalogo.sat",
        string="Método de Pago",
        domain=[("tipo", "=", "0")],
    )

    forma_pago_id = fields.Many2one(
        comodel_name="ev.catalogo.sat",
        string="Forma de Pago",
        domain=[("tipo", "=", "1")],
    )

    uso_cfdi_id = fields.Many2one(
        comodel_name="ev.catalogo.sat",
        string="Uso CFDI",
        domain=[("tipo", "=", "2")],
    )

    def _tipo_comprobante(self):
        return [
            ("I", "Ingreso"),
            ("E", "Egreso"),
            ("P", "Pago"),
            ("T", "Traslado"),
            ("N", "Nómina"),
            ("R", "Retención"),
        ]

    @api.onchange("metodo_pago_id")
    def _onchange_metodo_pago(self):
        
        _logger.warning(f"Metodo: {self.metodo_pago_id.clave}")
        self.forma_pago_id = False

        domain = [("tipo", "=", 1)]

        if self.metodo_pago_id:
            if self.metodo_pago_id.clave == "PPD":
                domain.append(("clave", "=", "99"))
            else:
                domain.append(("clave", "!=", "99"))
        _logger.warning(domain)
        return {"domain": {"forma_pago_id": domain}}

    @api.constrains("metodo_pago_id", "forma_pago_id")
    def _check_forma_pago(self):
        for rec in self:
            if rec.metodo_pago_id and rec.forma_pago_id:
                if (
                    rec.metodo_pago_id.clave == "PPD"
                    and rec.forma_pago_id.clave != "99"
                ):
                    raise ValidationError("Para PPD la forma de pago debe ser 99")

    @api.constrains("uuid")
    def _check_uuid(self):
        for rec in self:
            if rec.uuid:
                if not re.match(r"^[A-F0-9-]{36}$", rec.uuid, re.I):
                    raise ValidationError("UUID inválido")
