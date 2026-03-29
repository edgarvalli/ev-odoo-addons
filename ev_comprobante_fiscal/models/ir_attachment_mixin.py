from typing import List
from odoo import models, api
from ..types.ir_attachment_type import FileType
    
class IrAttachmentMixin(models.Model):
    _inherit = "ir.attachment"

    @api.model
    def create(self, vals: List[FileType]):
        
        record = super().create(vals)

        # Aquí detectas el archivo
        
        for file in vals:
            if file.get("res_model") == "account.move":
                if file.get("res_id"):
                    move = self.env["account.move"].browse(file["res_id"])

                    # 🔥 lógica aquí
                    print("Archivo adjuntado a factura:", move.name)

        return record
