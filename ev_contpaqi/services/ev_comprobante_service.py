from odoo.orm.environments import Environment
from .ev_cnomina_service import NominasService


class EVComprobanteService:
    env: Environment

    def __init__(self, env):
        self.env = env
        self.nominas = NominasService(env)