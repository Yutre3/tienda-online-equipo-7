from peewee import OperationalError, SqliteDatabase

import app
from negocio import TiendaServicio


def test_crear_servicio_inicializa_base_indicada() -> None:
    base = SqliteDatabase(":memory:", pragmas={"foreign_keys": 1})

    servicio = app.crear_servicio(base)

    assert isinstance(servicio, TiendaServicio)
    assert base.is_closed() is False
    assert {"clientes", "productos", "pedidos", "detalles_pedido"} <= set(
        base.get_tables()
    )
    base.close()


def test_crear_servicio_sin_mysql_usa_base_portatil_con_datos(
    monkeypatch, tmp_path
) -> None:
    ruta_base = tmp_path / "tienda_online.db"
    monkeypatch.setenv("DB_ENGINE", "sqlite")
    monkeypatch.setenv("SQLITE_PATH", str(ruta_base))

    servicio = app.crear_servicio()

    assert isinstance(app.base_datos_proxy.obj, SqliteDatabase)
    assert ruta_base.exists()
    assert [cliente.correo for cliente in servicio.listar_clientes()] == [
        "cliente@ejemplo.cl"
    ]
    assert {producto.sku for producto in servicio.listar_productos()} == {
        "AUD-001",
        "MOU-001",
        "TEC-001",
    }
    app.base_datos_proxy.close()


def test_main_informa_error_de_conexion(monkeypatch, capsys) -> None:
    def fallar():
        raise OperationalError("servidor no disponible")

    monkeypatch.setattr(app, "crear_servicio", fallar)

    resultado = app.main()

    salida = capsys.readouterr().out
    assert resultado == 1
    assert "No fue posible conectar" in salida
    assert "servidor no disponible" in salida


def test_main_informa_puerto_invalido_sin_traza(monkeypatch, capsys) -> None:
    monkeypatch.setenv("DB_PORT", "puerto-invalido")

    resultado = app.main()

    salida = capsys.readouterr().out
    assert resultado == 1
    assert "configuración" in salida.lower()
    assert "DB_PORT" in salida
