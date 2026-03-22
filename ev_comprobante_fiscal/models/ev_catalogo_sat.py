from odoo import models, fields


class EVCatalogoSAT(models.Model):
    _name = "ev.catalogo.sat"
    _description = "[EV] Catalogo SAT"
    _rec_name = "descripcion"

    clave = fields.Char("Clave")
    clave_texto = fields.Char("Clave Texto")
    descripcion = fields.Char("Descripción")
    persona_fisica = fields.Boolean("Persona Física")
    persona_moral = fields.Boolean("Persona Moral")
    retencion = fields.Boolean("Retención")
    traslado = fields.Boolean("Traslado")
    tipo = fields.Selection(selection="_tipo_catalogo", string="Tipo Catalogo")

    def _tipo_catalogo(self):
        return [
            (0, "Metodo de Pago"),
            (1, "Forma de Pago"),
            (2, "Uso de CFDI"),
            (3, "Impuestos"),
            (4, "Paises"),
            (5, "Tipo de CFDI"),
            (6,"Tipo de Relación - Cancelación")
        ]
