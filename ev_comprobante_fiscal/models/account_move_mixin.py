from odoo import models, fields, api

class AccountMoveMixin(models.Model):
    _inherit = "account.move"

    ev_comprobante_id = fields.Many2one(
        comodel_name="ev.comprobante.fiscal",
        string="Comprobante Fiscal"
    )
    
    ev_tipo = fields.Char("Tipo Comprobante", store=False)
    ev_uuid = fields.Char("UUID", store=False)
    ev_uso_cfdi_id = fields.Char("Uso de CFDI", store=False)
    ev_metodo_pago_id = fields.Char("Metodo De Pago", store=False)
    ev_forma_pago_id = fields.Char("Forma de Pago", store=False)

    def ev_timbrar_factura(self):
        rfc = self.env.company.vat
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
                "type": "success" if rfc else "error",
                "sticky": False,
            },
        }
    
    @api.model
    def create(self, vals):
        move = super().create(vals)

        # Solo para facturas (no asientos contables)
        if move.move_type in ['out_invoice', 'in_invoice']:
            comprobante = self.env['ev.comprobante.fiscal'].create({
                'tipo': 'I',  # puedes mapear esto dinámicamente
            })

            move.ev_comprobante_id = comprobante.id
            move.ev_forma_pago_id = comprobante.forma_pago_id.descripcion
            move.ev_metodo_pago_id = comprobante.metodo_pago_id.descripcion
            move.ev_tipo = comprobante.tipo
            move.ev_uso_cfdi_id = comprobante.uso_cfdi_id.descripcion
            move.ev_uuid = comprobante.uuid

        return move
