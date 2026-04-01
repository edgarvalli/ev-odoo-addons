from odoo import models, fields
from odoo.exceptions import UserError
from ..services.sync_contpaqi_service import SyncJobTitleService


class HrJobMixin(models.Model):
    _inherit = "hr.job"

    ev_idpuesto = fields.Integer("ID Puesto Contpaqi", index=True)

    def action_sync_job(self):
        try:
            srv = SyncJobTitleService(self.env)
            srv.sync()

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Éxito",
                    "message": "Puestos sincronizados",
                    "type": "success",
                },
            }

        except Exception as e:
            raise UserError(f"Ocurrio un error de sincronización: {e}") from e
