from odoo import models, fields


class EVInvDevices(models.Model):
    _name = "ev.inv.devices"
    _description = "EV - Dispositivos"
    _rec_name = "serial_number"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    serial_number = fields.Char("No. Serie", index=True)
    user_id = fields.Many2one(comodel_name="res.users", string="Usuario")
    type_id = fields.Many2one(comodel_name="ev.devices.type", string="Tipo")
    vendor_id = fields.Many2one(comodel_name="ev.inv.vendors", string="Fabricante")
    device_model_id = fields.Many2one(comodel_name="ev.devices.model", string="Modelo")
    hostname = fields.Char("Hostname")
    processor_id = fields.Many2one("ev.inv.processors", string="Procesador")
    os_id = fields.Many2one("ev.operative.system", string="Sistema Operativo")
    ram = fields.Char("RAM")
    storage = fields.Char("Almacenamiento")
    observation = fields.Text("Observaciones")
    purchase_date = fields.Datetime("Fecha de Compra")
    warranty_date = fields.Datetime("Fecha de Garantía")
    active = fields.Boolean("Activo")


class InvOperativeSystem(models.Model):
    _name = "ev.operative.system"
    _description = "EV - Sistemas Operativos"
    _rec_name = "name"

    brand_id = fields.Many2one("ev.inv.vendors", string="Marca")
    name = fields.Char("Sistema Operativo")


class InvProcessor(models.Model):
    _name = "ev.inv.processors"
    _description = "EV - Procesadores"
    _rec_name = "name"

    vendor_id = fields.Many2one("ev.inv.vendors", string="Fabricante")
    name = fields.Char("Nombre")


class DevicesModel(models.Model):
    _name = "ev.devices.model"
    _description = "EV - Modelo de equipos"
    _rec_name = "name"

    vendor_id = fields.Many2one("ev.inv.vendors", string="Fabricante")
    name = fields.Char("Modelo")


class EVInvVendors(models.Model):
    _name = "ev.inv.vendors"
    _description = "EV - Fabricantes"
    _rec_name = "vendor"

    vendor = fields.Char("Fabricante")


class InvDeviceType(models.Model):
    _name = "ev.devices.type"
    _description = "EV - Tipo de dispositivos"
    _rec_name = "type"

    type = fields.Char("Tipo")
