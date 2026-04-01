from odoo import fields, models
from odoo.exceptions import UserError
from ..services.sync_contpaqi_service import SyncEmployeesService


class HrEmployeeMixin(models.Model):
    """Extensión de res.company para ligar Odoo a Nominas Contpaqi"""

    _inherit = "hr.employee"

    ev_codigo = fields.Char("No. Empleado")
    ev_idempleado = fields.Integer("ID Contpaqi Nóminas", index=True)

    def action_sync_employee(self):
        try:
            srv = SyncEmployeesService(self.env)
            srv.sync()
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Éxito",
                    "message": "Empleados sincronizados",
                    "type": "success",
                },
            }
        except Exception as e:
            raise UserError(f"Ocurrio un error de sincronización: {e}") from e
