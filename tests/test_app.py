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
