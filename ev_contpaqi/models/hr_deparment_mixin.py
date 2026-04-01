from odoo import models, fields
from odoo.exceptions import UserError


class HrDeparmentMixin(models.Model):
    _inherit = "hr.department"

    ev_iddepartamento = fields.Integer("ID Nominas Contpaqi")

    def action_sync_contpaqi(self):
        self.sync_contpaqi_nominas()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Éxito",
                "message": "Departamentos sincronizados",
                "type": "success",
            },
        }

    def sync_empleados_nominas(self):

        return

    def sync_contpaqi_nominas(self):
        dbname = self.env.company.ev_contpaqi_nominas_db.dbname

        if not dbname:
            raise UserError(
                "Debe de definir la base de datos de nominas en la compañia."
            )

        sql = """
            SELECT iddepartamento, descripcion
            FROM nom10003
            WHERE iddepartamento > 1;
        """

        with self.env["ev.tools.mssql"].connect(dbname) as db:
            deptos: list[dict] = db.fetchall(sql) or []

        dept_model = self.env["hr.department"].sudo()

        ids = [int(d["iddepartamento"]) for d in deptos]
        existing = dept_model.search([("ev_iddepartamento", "in", ids)])
        mapped = {rec.ev_iddepartamento: rec for rec in existing}

        for depto in deptos:
            dept_id = int(depto.get("iddepartamento") or 0)
            name = depto.get("descripcion", "")

            if dept_id in mapped:
                rec = mapped[dept_id]
                if rec.name != name:
                    rec.write({"name": name})
            else:
                dept_model.create(
                    {
                        "name": name,
                        "ev_iddepartamento": dept_id,
                    }
                )
