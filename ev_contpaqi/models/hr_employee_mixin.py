from odoo import fields, models
from odoo.exceptions import UserError


class HrEmployeeMixin(models.Model):
    """Extensión de res.company para ligar Odoo a Nominas Contpaqi"""

    _inherit = "hr.employee"

    ev_codigo = fields.Char("No. Empleado")
    ev_idempleado = fields.Integer("ID Contpaqi Nóminas", index=True)

    def _prepare_employee_vals(self, row: dict):
        dept = (
            self.env["hr.department"]
            .sudo()
            .search(
                [("ev_iddepartamento", "=", int(row.get("iddepartamento") or 0))],
                limit=1,
            )
        )

        full_name = " ".join(
            filter(
                None,
                [
                    row.get("nombre"),
                    row.get("apellidopaterno"),
                    row.get("apellidomaterno"),
                ],
            )
        )

        return {
            "name": full_name,
            "work_email": row.get("email"),
            "department_id": dept.id if dept else False,
            "ev_codigo": row.get("codigoempleado"),
        }

    def sync_contpaqi_employees(self):
        dbname = self.env.company.ev_contpaqi_nominas_db.dbname

        if not dbname:
            raise UserError("Debe definir la DB de nóminas.")

        sql = """
            SELECT
                idempleado,
                codigoempleado,
                nombre,
                apellidopaterno,
                apellidomaterno,
                iddepartamento
            FROM nom10001 WHERE EstadoEmpleado <> 'B';
        """

        with self.env["ev.tools.mssql"].connect(dbname) as db:
            empleados = db.fetchall(sql) or []

        emp_model = self.env["hr.employee"].sudo()

        ids = [int(x["idempleado"]) for x in empleados]
        existing = emp_model.search([("ev_idempleado", "in", ids)])
        mapped = {x.ev_idempleado: x for x in existing}

        for row in empleados:
            emp_id = int(row.get("idempleado") or 0)

            vals = self._prepare_employee_vals(row)

            if emp_id in mapped:
                mapped[emp_id].write(vals)
            else:
                vals["ev_idempleado"] = emp_id
                emp_model.create(vals)

    def action_sync_employee(self):
        self.sync_contpaqi_employees()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Éxito",
                "message": "Empleados sincronizados",
                "type": "success",
            },
        }
