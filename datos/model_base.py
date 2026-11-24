"""Base compartida por todos los modelos Peewee de la tienda."""

from peewee import Model

from datos.conexion import base_datos_proxy


class ModelBase(Model):
    class Meta:
        database = base_datos_proxy


# Compatibilidad con el nombre utilizado por versiones anteriores.
ModeloBase = ModelBase


__all__ = ["ModelBase", "ModeloBase"]
