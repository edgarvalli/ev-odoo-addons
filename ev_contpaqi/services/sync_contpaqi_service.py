from dataclasses import dataclass
from odoo.orm.environments import Environment
from ..types.nominas_type import DeparmentDict, EmpleadoDict, JobDict
from ..types.typing import HrEmployee, HrDepartment, HrJob


@dataclass(slots=True)
class SyncJobTitleService:
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


@dataclass(slots=True)
class SyncDepartmentService:
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


@dataclass(slots=True)
class SyncEmployeesService:
    env: Environment

    def _get_employees_from_sql(self) -> list[EmpleadoDict]:

        dbname = self.env.company.ev_contpaqi_nominas_db.dbname

        if not dbname:
            raise ValueError("Debe definir la DB de nóminas.")

        sql = """
            SELECT
                idempleado,
                idpuesto,
                iddepartamento,
                codigoempleado,
                CONCAT_WS(' ', nombre,apellidopaterno, apellidomaterno) nombre,
                REPLACE(correoelectronico,';',',') email,
                numerosegurosocial nss,
                CASE
                    WHEN sexo = 'M' THEN 'male'
                    WHEN sexo = 'F' THEN 'female'
                    ELSE 'other'
                END sexo,
                CASE
                    WHEN estadocivil = 'C' THEN 'married'
                    WHEN estadocivil = 'S' THEN 'single'
                    WHEN estadocivil = 'V' THEN 'widower'
                    WHEN estadocivil = 'D' THEN 'divorced'
                END AS estadocivil,
                fechanacimiento,
                fechaalta,
                fechabaja,
                sueldodiario,
                sueldointegrado,
                sueldobaseliquidacion
            FROM nom10001 WHERE EstadoEmpleado <> 'B';
        """

        try:
            with self.env["ev.tools.mssql"].connect(dbname) as db:
                return db.fetchall(sql) or []
        except Exception as e:
            raise ValueError(f"Error al obtener empleados desde {dbname}: {e}") from e

    def _get_mapped_exists(self, ids: list[int]) -> dict[int, HrEmployee]:
        hr_employee = self.env["hr.employee"].sudo()
        employee_exists = hr_employee.search([("ev_idempleado", "in", ids)])
        return {e.ev_idempleado: e for e in employee_exists}

    def _get_departments_map(self, ids: list[int]) -> dict[int, HrDepartment]:
        departments = (
            self.env["hr.department"].sudo().search([("ev_iddepartamento", "in", ids)])
        )
        return {d.ev_iddepartamento: d for d in departments}

    def _get_jobs_map(self, ids: list[int]) -> dict[int, HrJob]:
        jobs = self.env["hr.job"].sudo().search([("ev_idpuesto", "in", ids)])
        return {j.ev_idpuesto: j for j in jobs}

    def _prepare_data(
        self,
        empleado: EmpleadoDict,
        dept_map: dict[int, HrDepartment],
        jobs_map: dict[int, HrJob],
    ) -> dict:
        dept = dept_map.get(empleado["iddepartamento"])
        job = jobs_map.get(empleado["idpuesto"])

        return {
            "name": empleado["nombre"],
            "department_id": dept.id if dept else False,
            "job_id": job.id if job else False,
            "ev_codigo": empleado["codigoempleado"],
            "ssnid": empleado["nss"],
            "birthday": empleado["fechanacimiento"],
            "sex": empleado["sexo"],
            "wage": empleado["sueldointegrado"],
        }

    def sync(self):

        job_srv = SyncJobTitleService(self.env)
        depto_srv = SyncDepartmentService(self.env)

        job_srv.sync()
        depto_srv.sync()

        # Obteniendo empleados de SQL
        empleados = self._get_employees_from_sql()
        ids = [int(e["idempleado"]) for e in empleados]

        # Obteniendo empleados de Odoo
        hr_employee = self.env["hr.employee"].sudo()
        employee_mapped = self._get_mapped_exists(ids)

        # Obteniendo departamentos
        dept_ids = list({e["iddepartamento"] for e in empleados if e["iddepartamento"]})
        dept_map = self._get_departments_map(dept_ids)

        # Obteniendo puestos
        job_ids = list({e["idpuesto"] for e in empleados if e["idpuesto"]})
        jobs_map = self._get_jobs_map(job_ids)

        for e in empleados:
            idempleado = e.get("idempleado")
            vals = self._prepare_data(e, dept_map, jobs_map)
            if idempleado in employee_mapped:
                employee_mapped[idempleado].write(vals)
            else:
                vals["ev_idempleado"] = idempleado
                hr_employee.create(vals)
