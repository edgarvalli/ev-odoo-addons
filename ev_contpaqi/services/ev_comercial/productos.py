from ..contpaqi_orm import ContpaqiORM


class ComercialProductos(ContpaqiORM):
    TABLENAME = "admProductos"
    PRIMARY_KEY = "CIDPRODUCTO"
    SISTEMA = "comercial"
