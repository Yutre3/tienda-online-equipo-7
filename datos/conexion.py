"""Inicialización de la base Peewee para producción y pruebas."""

from peewee import Database, DatabaseProxy, MySQLDatabase

from datos.configuracion import ConfiguracionBaseDatos


base_datos_proxy = DatabaseProxy()


def configurar_base_datos(base: Database | None = None) -> Database:
    if base is None:
        datos = ConfiguracionBaseDatos.desde_entorno()
        base = MySQLDatabase(
            datos.nombre,
            host=datos.servidor,
            port=datos.puerto,
            user=datos.usuario,
            password=datos.contrasena,
            charset="utf8mb4",
        )
    base_datos_proxy.initialize(base)
    return base


def tablas() -> tuple[type, ...]:
    from datos.modelos.models import (
        ClienteModelo,
        DetallePedidoModelo,
        PedidoModelo,
        ProductoModelo,
    )

    return ClienteModelo, ProductoModelo, PedidoModelo, DetallePedidoModelo


def crear_tablas() -> None:
    base_datos_proxy.create_tables(tablas(), safe=True)
