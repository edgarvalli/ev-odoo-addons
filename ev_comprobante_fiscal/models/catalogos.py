from odoo import fields, models

class CatalogoFormaDePago(models.Model):
    """Catalogo de forma de pago SAT"""
    
    _name = "ev.sat.forma.pago"
    _description = "Catalogo de Forma de pago SAT"
    
    clave = fields.Char("Clave")
    descripcion = fields.Text("Descripcion")

class CatalogoImpuestos(models.Model):
    """Modelo para mostrar los catalogos de impuestos"""
    
    _name = "ev.sat.catalogo.impuestos"
    _description = "Catalogo de impuestos SAT"
    
    clave = fields.Char("Clave")
    descripcion = fields.Text("Descripción")
    retencion = fields.Boolean("Retención")
    traslado = fields.Boolean("Traslado")