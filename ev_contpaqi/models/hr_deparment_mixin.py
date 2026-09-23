from odoo import models, fields
from odoo.exceptions import UserError
from ..services.ev_nominas import SyncDepartments


class HrDeparmentMixin(models.Model):
    _inherit = "hr.department"

    ev_iddepartamento = fields.Integer("ID Nominas Contpaqi")

    def action_sync_departments(self):
        try:
            srv = SyncDepartments(self.env)
            srv.sync()
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Éxito",
                    "message": "Departamentos sincronizados",
                    "type": "success",
                },
            }
        except Exception as e:
            raise UserError(f"Ocurrio un error de sincronización: {e}") from e
