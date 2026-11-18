from peewee import SqliteDatabase

from datos.conexion import configurar_base_datos, crear_tablas
from verificar_base_datos import main


def test_verificador_confirma_las_seis_tablas_de_la_entrega(
    tmp_path, monkeypatch, capsys
) -> None:
    ruta = tmp_path / "tienda_verificacion.db"
    base = SqliteDatabase(ruta, pragmas={"foreign_keys": 1})
    configurar_base_datos(base)
    base.connect()
    crear_tablas()
    base.close()

    monkeypatch.setenv("DB_ENGINE", "sqlite")
    monkeypatch.setenv("SQLITE_PATH", str(ruta))

    assert main() == 0
    salida = capsys.readouterr().out
    for tabla in (
        "paises",
        "usuarios",
        "clientes",
        "productos",
        "pedidos",
        "detalles_pedido",
    ):
        assert f"{tabla}: 0 registros" in salida
    assert "se encontraron las seis tablas" in salida
