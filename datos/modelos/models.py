"""Mapeo Peewee de las entidades de la tienda en línea."""

from datetime import datetime

from peewee import (
    AutoField,
    BigIntegerField,
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    TextField,
)

from datos.model_base import ModelBase, ModeloBase


class PaisModelo(ModelBase):
    id_pais = AutoField()
    pais = CharField(max_length=50, unique=True)
    nacionalidad = CharField(max_length=50, null=True)
    iso2 = CharField(max_length=2, unique=True)
    iso3 = CharField(max_length=3, unique=True)
    habilitado = BooleanField(default=True, index=True)

    class Meta:
        table_name = "paises"


class UsuarioModelo(ModelBase):
    id_usuario = AutoField()
    rut = CharField(max_length=12, unique=True)
    nombre = CharField(max_length=25)
    apellido = CharField(max_length=25)
    correo = CharField(max_length=191, unique=True)
    pais = ForeignKeyField(
        PaisModelo,
        backref="usuarios",
        column_name="pais",
        on_delete="RESTRICT",
        on_update="CASCADE",
    )
    fecha_nacimiento = DateField()
    genero = IntegerField()
    fecha_incorporacion = DateField(default=datetime.now)
    habilitado = BooleanField(default=True, index=True)
    password = CharField(max_length=60)

    class Meta:
        table_name = "usuarios"


class ClienteModelo(ModelBase):
    id = AutoField()
    nombre = CharField(max_length=120)
    correo = CharField(max_length=190, unique=True)
    creado_en = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "clientes"


class ProductoModelo(ModelBase):
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


class PedidoModelo(ModelBase):
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


class DetallePedidoModelo(ModelBase):
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
