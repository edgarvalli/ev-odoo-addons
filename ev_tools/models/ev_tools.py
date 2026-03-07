from odoo import models
from ..services.mssql import SqlServer


class EVTools(models.AbstractModel):
    _name = "ev.tools"