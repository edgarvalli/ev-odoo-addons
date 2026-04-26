from odoo import fields, models


class EVDev(models.Model):
    _name = "ev.dev"
    _description = "Modulo para desarrollar"

    name = fields.Char("Nombre")
    user_id = fields.Many2one("res.users", string="Usuarios")
