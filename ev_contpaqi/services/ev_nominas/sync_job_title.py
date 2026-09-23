from dataclasses import dataclass
from odoo.orm.environments import Environment

from .types import JobDict
from .type_typing import HrJob


@dataclass(slots=True)
class SyncJobTitle:
    env: Environment

    def _get_jobs_from_sql(self) -> list[JobDict]:
        dbname = self.env.company.ev_contpaqi_nominas_db.dbname
        sql = (
            "SELECT idpuesto,numeropuesto,descripcion FROM nom10006 WHERE idpuesto > 1;"
        )

        try:
            with self.env["ev.tools.mssql"].connect(dbname) as db:
                return db.fetchall(sql) or []
        except Exception as e:
            raise ValueError(f"Ocurrio un error al buscar puestos {dbname}: {e}") from e

    def _get_mapped_exists(self, ids: list[int]) -> dict[int, HrJob]:
        job_model = self.env["hr.job"].sudo()
        jobs = job_model.search([("ev_idpuesto", "in", ids)])
        return {j.ev_idpuesto: j for j in jobs}

    def sync(self):
        jobs = self._get_jobs_from_sql()

        if not jobs:
            return

        ids = [int(j["idpuesto"]) for j in jobs]
        jobs_mapped = self._get_mapped_exists(ids)

        job_model = self.env["hr.job"].sudo()

        for job in jobs:

            job_id = job["idpuesto"]
            name = job["descripcion"]

            existing = jobs_mapped.get(job_id)

            if existing:
                if existing.name != name:
                    existing.write({"name": name})
            else:
                job_model.create({"name": name, "ev_idpuesto": job_id})
