"""Inicialización de la base Peewee para producción y pruebas."""

from contextlib import AbstractContextManager

from peewee import CharField, Database, DatabaseProxy, MySQLDatabase, SqliteDatabase
from playhouse.migrate import SchemaMigrator, migrate

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
    migrar_esquema()
    base_datos_proxy.create_tables(tablas(), safe=True)


def migrar_esquema() -> None:
    """Actualiza de forma conservadora estructuras creadas por versiones previas."""
    base = base_datos_proxy.obj
    if "productos" not in base.get_tables():
        return
    columnas = {columna.name for columna in base.get_columns("productos")}
    if "sku" in columnas:
        return

    migrador = SchemaMigrator.from_database(base)
    migrate(migrador.add_column("productos", "sku", CharField(max_length=50, null=True)))
    filas = base.execute_sql("SELECT id FROM productos ORDER BY id").fetchall()
    for (identificador,) in filas:
        base.execute_sql(
            "UPDATE productos SET sku = ? WHERE id = ?"
            if isinstance(base, SqliteDatabase)
            else "UPDATE productos SET sku = %s WHERE id = %s",
            (f"LEGACY-{identificador:06d}", identificador),
        )
    migrate(
        migrador.add_not_null("productos", "sku"),
        migrador.add_index("productos", ("sku",), unique=True),
    )


def transaccion_escritura() -> AbstractContextManager:
    """Abre una transacción que serializa escrituras también durante pruebas."""
    base = base_datos_proxy.obj
    if isinstance(base, SqliteDatabase):
        return base.atomic("IMMEDIATE")
    return base.atomic()
