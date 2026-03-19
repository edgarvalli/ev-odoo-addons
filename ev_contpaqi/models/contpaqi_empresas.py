from odoo import models, fields


class EVContpaqiEmpresas(models.Model):
    _name = "ev.contpaqi.empresas"
    _description = "Contpaqi Empresas"

    _sql_constraints = [
        ("uniq_db_origin", "unique(dbname, system_origin)", "Ya existe esta empresa.")
    ]

    name = fields.Char("Empresa")
    dbname = fields.Char("Base de Datos")
    system_origin = fields.Selection(
        string="Sistema Origen",
        selection=[
            ("contabilidad", "Contabilidad"),
            ("comercial", "Comercial"),
            ("nominas", "Nominas"),
        ],
    )

    def sync_nominas(self):
        nominas = self.env["ev.contpaqi.nominas"]
        empresas = nominas.empresas(fields="NombreEmpresa name, RutaEmpresa dbname")

        for e in empresas:
            record = self.search(
                [("dbname", "=", e["dbname"]), ("system_origin", "=", "nominas")],
                limit=1,
            )

            vals = {
                "name": e["name"],
                "dbname": e["dbname"],
                "system_origin": "nominas",
            }

            if record:
                record.write(vals)
            else:
                self.create(vals)

    def sync_comercial(self):
        comercial = self.env["ev.contpaqi.comercial"]
        empresas = comercial.empresas()

        for e in empresas:

            record = self.search(
                [("dbname", "=", e["dbname"]), ("system_origin", "=", "comercial")],
                limit=1,
            )

            vals = {
                "name": e["empresa"],
                "dbname": e["dbname"],
                "system_origin": "comercial",
            }

            if record:
                record.write(vals)
            else:
                self.create(vals)

    def action_sync(self):
        self.sync_comercial()
        self.sync_nominas()
