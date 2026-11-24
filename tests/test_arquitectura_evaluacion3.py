from peewee import Model

from datos.conexion import base_datos_proxy
from datos.model_base import ModelBase, ModeloBase
from datos.modelos import (
    ClienteModelo,
    DetallePedidoModelo,
    PaisModelo,
    PedidoModelo,
    ProductoModelo,
    UsuarioModelo,
)


def test_model_base_es_unico_y_usa_la_conexion_compartida() -> None:
    assert ModelBase is ModeloBase
    assert issubclass(ModelBase, Model)
    assert ModelBase._meta.database is base_datos_proxy


def test_todos_los_modelos_heredan_directamente_de_model_base() -> None:
    modelos = (
        PaisModelo,
        UsuarioModelo,
        ClienteModelo,
        ProductoModelo,
        PedidoModelo,
        DetallePedidoModelo,
    )

    assert all(ModelBase in modelo.__bases__ for modelo in modelos)
