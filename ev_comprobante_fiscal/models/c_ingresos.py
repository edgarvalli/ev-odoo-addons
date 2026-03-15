from odoo import fields, models


class ComprobanteIngresos(models.Model):
    """Modelo de comprobante de ingresos"""

    version = fields.Selection(
        "Version", selection=[("3.0", "Version 3.0"), ("4.0", "Version 4.0")]
    )
