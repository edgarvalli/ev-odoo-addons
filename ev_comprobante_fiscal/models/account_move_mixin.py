from odoo import models, fields, api


class AccountMoveMixin(models.Model):
    _inherit = "account.move"

    ev_estatus = fields.Selection(
        related="ev_comprobante_id.estatus",
        string="Estatus",
        readonly=True,
        store=False,
    )

    ev_comprobante_id = fields.Many2one(
        comodel_name="ev.comprobante.fiscal", string="Comprobante Fiscal"
    )
    ev_tipo = fields.Char("Tipo Comprobante", store=False)
    ev_forma_pago_id = fields.Many2one(
        "ev.catalogo.sat",
        related="ev_comprobante_id.forma_pago_id",
        readonly=False,
        store=False,
    )

    ev_metodo_pago_id = fields.Many2one(
        "ev.catalogo.sat",
        related="ev_comprobante_id.metodo_pago_id",
        readonly=False,
        store=False,
    )

    ev_uso_cfdi_id = fields.Many2one(
        "ev.catalogo.sat",
        related="ev_comprobante_id.uso_cfdi_id",
        readonly=False,
        store=False,
    )

    ev_forma_pago_domain = fields.Binary(
        "Forma de Pago Domain", compute="_forma_pago_compute"
    )

    #### API ####

    @api.model
    def create(self, vals):
        inv = super().create(vals)

        # Solo para facturas (no asientos contables)
        if inv.move_type in ["out_invoice", "in_invoice"]:
            comprobante = self.env["ev.comprobante.fiscal"].create(
                {
                    "tipo": "I",
                    "forma_pago_id": inv.ev_forma_pago_id,
                    "metodo_pago_id": inv.ev_metodo_pago_id,
                    "uso_cfdi_id": inv.ev_uso_cfdi_id,
                }
            )

            inv.ev_comprobante_id = comprobante.id

        return inv

    @api.model
    def write(self, vals):
        res = super().write(vals)

        for rec in self:
            if rec.ev_estatus == "sin_timbrar" and rec.ev_comprobante_id:
                rec.ev_comprobante_id.write(
                    {
                        "forma_pago_id": rec.ev_forma_pago_id,
                        "metodo_pago_id": rec.ev_metodo_pago_id,
                        "uso_cfdi_id": rec.ev_uso_cfdi_id,
                    }
                )

        return res

    ### COMPUTES ###

    @api.onchange("ev_metodo_pago_id")
    def _forma_pago_compute(self):
        for rec in self:
            domain = [("tipo", "=", 1)]

            if not rec.ev_metodo_pago_id:
                rec.ev_forma_pago_domain = domain
                return

            if rec.ev_metodo_pago_id.clave == "PPD":
                domain.append(("clave", "=", "99"))
            else:
                domain.append(("clave", "!=", "99"))

            rec.ev_forma_pago_domain = domain

    ### ACTIONS ###

    def ev_timbrar_factura(self):
        rfc = self.env.company.vat

        for rec in self:
            rec.ev_comprobante_id.estatus = "timbrado"
            rec.ev_comprobante_id.uuid = "42298429-c103-4838-8e1b-ac8b40555884"

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Timbrado de Factura" if rfc else "Ocurrio un problema",
                "message": (
                    f"Timbrado de prueba con rfc {rfc}"
                    if rfc
                    else "Debe de definir el RFC"
                ),
                "type": "success" if rfc else "danger",
                "sticky": False,
            },
        }

    def ev_cancelar_factura(self):
        
        rfc = self.env.company.vat
        
        for rec in self:
            rec.ev_comprobante_id.estatus = "cancelado"

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Cancelado de timbre de Factura" if rfc else "Ocurrio un problema",
                "message": (
                    f"Se ha cancelado la factura con UUID {rec.ev_comprobante_id.uuid}"
                    if rfc
                    else "Debe de definir el RFC"
                ),
                "type": "danger",
                "sticky": False,
            },
        }
