"""Mapeo Peewee de las entidades de la tienda en línea."""

from datetime import datetime

from peewee import (
    AutoField,
    BigIntegerField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
    TextField,
)

from datos.conexion import base_datos_proxy


class ModeloBase(Model):
    class Meta:
        database = base_datos_proxy


class ClienteModelo(ModeloBase):
    id = AutoField()
    nombre = CharField(max_length=120)
    correo = CharField(max_length=190, unique=True)
    creado_en = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "clientes"


class ProductoModelo(ModeloBase):
    id = AutoField()
    sku = CharField(max_length=50, unique=True)
    nombre = CharField(max_length=150, index=True)
    descripcion = TextField(default="")
    precio_centavos = BigIntegerField()
    stock = IntegerField(default=0)
    creado_en = DateTimeField(default=datetime.now)
    actualizado_en = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "productos"


class PedidoModelo(ModeloBase):
    id = AutoField()
    cliente = ForeignKeyField(
        ClienteModelo,
        backref="pedidos",
        column_name="cliente_id",
        on_delete="RESTRICT",
        on_update="CASCADE",
    )
    estado = CharField(max_length=20, default="CREADO", index=True)
    total_centavos = BigIntegerField(default=0)
    creado_en = DateTimeField(default=datetime.now)
    actualizado_en = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "pedidos"


class DetallePedidoModelo(ModeloBase):
    id = AutoField()
    pedido = ForeignKeyField(
        PedidoModelo,
        backref="detalles",
        column_name="pedido_id",
        on_delete="CASCADE",
        on_update="CASCADE",
    )
    producto = ForeignKeyField(
        ProductoModelo,
        backref="detalles_pedido",
        column_name="producto_id",
        on_delete="RESTRICT",
        on_update="CASCADE",
    )
    cantidad = IntegerField()
    precio_unitario_centavos = BigIntegerField()
    subtotal_centavos = BigIntegerField()

    class Meta:
        table_name = "detalles_pedido"
        indexes = ((('pedido', 'producto'), True),)
