import pytest
from peewee import SqliteDatabase

from datos.conexion import configurar_base_datos, crear_tablas, tablas


@pytest.fixture()
def base_pruebas():
    base = SqliteDatabase(":memory:", pragmas={"foreign_keys": 1})
    configurar_base_datos(base)
    base.connect()
    crear_tablas()
    yield base
    base.drop_tables(list(reversed(tablas())))
    base.close()
