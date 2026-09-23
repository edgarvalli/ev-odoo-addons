from dataclasses import dataclass
from odoo.orm.environments import Environment

from .types import DeparmentDict
from .type_typing import HrDepartment


@dataclass(slots=True)
class SyncDepartments:
    env: Environment

    def _get_departments_from_sql(self) -> list[DeparmentDict]:
        dbname = self.env.company.ev_contpaqi_nominas_db.dbname

        if not dbname:
            raise ValueError(
                "Debe de definir la base de datos de nominas en la compañia."
            )

        sql = """
            SELECT iddepartamento, descripcion
            FROM nom10003
            WHERE iddepartamento > 1;
        """

        try:
            with self.env["ev.tools.mssql"].connect(dbname) as db:
                return db.fetchall(sql) or []
        except Exception as e:
            raise ValueError(
                f"Ocurrio un error al buscar departamentos {dbname}: {e}"
            ) from e

    def _get_mapped_exists(self, ids: list[int]) -> dict[int, HrDepartment]:
        dept_model = self.env["hr.department"].sudo()
        depts = dept_model.search([("ev_iddepartamento", "in", ids)])
        return {d.ev_iddepartamento: d for d in depts}

    def sync(self):
        # Se obtienendo los departamentos de Contpaqi
        deptos = self._get_departments_from_sql()

        if not deptos:
            return

        ids = [int(d["iddepartamento"]) for d in deptos]

        # Se obtienendo los departamentos de Odoo
        deptos_mapped = self._get_mapped_exists(ids)

        depto_model = self.env["hr.department"].sudo()

        for dept in deptos:
            dept_id = dept["iddepartamento"]
            name = dept["descripcion"]

            existing = deptos_mapped.get(dept_id)

            if existing:
                if existing.name != name:
                    existing.write({"name": name})
            else:
                depto_model.create(
                    {
                        "ev_iddepartamento": dept_id,
                        "name": name,
                    }
                )
