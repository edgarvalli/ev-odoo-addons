from odoo.api import Environment
from odoo.exceptions import UserError
from typing import Literal
from ..tools.contpaqi_tools import get_dbname


class ContpaqiORM:
    SISTEMA: Literal["contabilidad", "comercial", "nominas"] = None
    TABLENAME: str = None
    PRIMARY_KEY: str = None

    def __init__(self, env: Environment):
        self.env = env
        self._build_dbname()

    def _build_dbname(self):
        if self.SISTEMA:
            dbname = get_dbname(self.env, self.SISTEMA)
            self.dbname = dbname

    def _build_conditions(self, domain: list[tuple]) -> tuple:
        allowed_operators = {
            "=",
            "!=",
            ">",
            "<",
            ">=",
            "<=",
            "LIKE",
            "IN",
        }
        conditions = []
        conditions_values = []
        for d in domain:
            if len(d) != 3:
                continue
            field, operator, value = d
            operator = operator.upper()
            if operator not in allowed_operators:
                raise UserError(f"Operador inválido: {operator}")

            if operator == "IN":
                placeholders = ",".join("?" for _ in value)
                conditions.append(f"{field} IN ({placeholders})")
                conditions_values.extend(value)
            else:
                conditions.append(f"{field} {operator} ?")
                conditions_values.append(value)

        return conditions, conditions_values

    def _make_record(self, data: dict):
        record = self.__class__(self.env)

        for key, value in data.items():
            setattr(record, key, value)

        return record

    def to_dict(
        self,
        fields: list[str] | None = None,
    ) -> dict:

        if not fields:

            return {
                key: value
                for key, value in self.__dict__.items()
                if not key.startswith("_") and key != "env"
            }

        result = {}

        for field in fields:

            parts = field.split(maxsplit=1)

            column = parts[0]

            alias = parts[1] if len(parts) > 1 else column

            result[alias] = getattr(self, column, None)

        return result

    def search(
        self,
        domain: list[tuple] | None = None,
        fields: list[str] | None = None,
        limit: int = 50,
        offset=0,
        order=None,
    ):

        fields = fields or ["*"]

        limit = int(limit or 50)

        conditions = []
        conditions_values = []

        if domain:
            conditions, conditions_values = self._build_conditions(domain)

        condition_str = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        top_clause = f"TOP {limit}" if not order else ""

        sql = f"""
            SELECT {top_clause}
                {",".join(fields)}
            FROM {self.TABLENAME}
            {condition_str}
        """

        if order:
            sql += f"""
                ORDER BY {order}
                OFFSET {offset} ROWS
                FETCH NEXT {limit} ROWS ONLY
            """

        try:

            with self.env["ev.tools.mssql"].connect(self.dbname) as db:

                if limit == 1:
                    row = db.fetchone(sql, tuple(conditions_values))
                    if not row:
                        return None
                    return self._make_record(row)

                rows = db.fetchall(sql, tuple(conditions_values))
                if not rows:
                    return None

                return [self._make_record(row) for row in rows]

        except Exception as e:
            raise UserError(str(e))

    def browse(self, record_id: int) -> "ContpaqiORM":
        result: dict = self.search([(self.PRIMARY_KEY, "=", record_id)], limit=1)

        if not result:
            raise UserError("No se encontro el registro buscado")

        return self._make_record(result)

    def create(self, values: dict) -> "ContpaqiORM":
        if not values:
            raise UserError("No hay valores para insertar")

        fields = list(values.keys())

        placeholders = ",".join("?" for _ in fields)

        sql = f"""
            INSERT INTO {self.TABLENAME}
            ({",".join(fields)})
            OUTPUT INSERTED.{self.PRIMARY_KEY}
            VALUES ({placeholders})
        """

        try:

            with self.env["ev.tools.mssql"].connect(self.dbname) as db:

                result = db.fetchone(
                    sql,
                    tuple(values.values()),
                )

                if not result:
                    raise UserError("No se pudo crear el registro")

                record_id = result[self.PRIMARY_KEY]

                return self.browse(record_id)

        except Exception as e:
            raise UserError(str(e))

    def update(
        self,
        record_id: int,
        values: dict,
    ) -> "ContpaqiORM":

        if not values:
            raise UserError("No hay valores para actualizar")

        set_clause = ",".join(f"{field} = ?" for field in values.keys())

        sql = f"""
            UPDATE {self.TABLENAME}
            SET {set_clause}
            WHERE {self.PRIMARY_KEY} = ?
        """

        params = list(values.values())

        params.append(record_id)

        try:

            with self.env["ev.tools.mssql"].connect(self.dbname) as db:

                db.execute(
                    sql,
                    tuple(params),
                )

                return self.browse(record_id)

        except Exception as e:
            raise UserError(str(e))
