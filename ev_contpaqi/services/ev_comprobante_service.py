from odoo.orm.environments import Environment
from .ev_comprobante_nomina_service import ComprobanteNominaService


class EVComprobanteService:
    env: Environment

    def __init__(self, env):
        self.env = env
        self.nominas = ComprobanteNominaService(env)
