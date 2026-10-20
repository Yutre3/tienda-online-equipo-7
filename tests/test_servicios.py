import pytest
from concurrent.futures import ThreadPoolExecutor
from peewee import SqliteDatabase

from datos.conexion import configurar_base_datos, crear_tablas
from negocio import Cliente, ErrorDominio, EstadoPedido, Producto, TiendaServicio


def preparar_tienda() -> tuple[TiendaServicio, Cliente, Producto]:
    servicio = TiendaServicio()
    cliente = servicio.registrar_cliente(Cliente("Ana", "ana@ejemplo.cl"))
    producto = servicio.registrar_producto(
        Producto("MOU-1", "Mouse", "Óptico", 1000, 5)
    )
    return servicio, cliente, producto


def test_crud_expuesto_por_servicio(base_pruebas) -> None:
    servicio, cliente, producto = preparar_tienda()

    cliente.nombre = "Ana María"
    producto.stock = 7
    servicio.actualizar_cliente(cliente)
    servicio.actualizar_producto(producto)

    assert servicio.listar_clientes()[0].nombre == "Ana María"
    assert servicio.listar_productos()[0].stock == 7
    servicio.eliminar_producto(producto.id)
    servicio.eliminar_cliente(cliente.id)
    assert servicio.listar_clientes() == []
    assert servicio.listar_productos() == []


def test_agregar_producto_descuenta_stock_y_actualiza_total(base_pruebas) -> None:
    servicio, cliente, producto = preparar_tienda()
    pedido = servicio.crear_pedido(cliente.id)

    actualizado = servicio.agregar_producto(pedido.id, producto.id, 2)

    assert actualizado.total_centavos == 2000
    assert actualizado.detalles[0].cantidad == 2
    assert servicio.obtener_producto(producto.id).stock == 3


def test_stock_insuficiente_no_altera_pedido_ni_producto(base_pruebas) -> None:
    servicio, cliente, producto = preparar_tienda()
    pedido = servicio.crear_pedido(cliente.id)

    with pytest.raises(ErrorDominio, match="stock"):
        servicio.agregar_producto(pedido.id, producto.id, 6)

    assert servicio.obtener_producto(producto.id).stock == 5
    assert servicio.obtener_pedido(pedido.id).detalles == []


def test_quitar_producto_repone_stock(base_pruebas) -> None:
    servicio, cliente, producto = preparar_tienda()
    pedido = servicio.crear_pedido(cliente.id)
    servicio.agregar_producto(pedido.id, producto.id, 2)

    actualizado = servicio.quitar_producto(pedido.id, producto.id)

    assert actualizado.detalles == []
    assert actualizado.total_centavos == 0
    assert servicio.obtener_producto(producto.id).stock == 5


def test_confirmar_bloquea_nuevos_productos(base_pruebas) -> None:
    servicio, cliente, producto = preparar_tienda()
    pedido = servicio.crear_pedido(cliente.id)
    servicio.agregar_producto(pedido.id, producto.id, 1)

    confirmado = servicio.confirmar_pedido(pedido.id)

    assert confirmado.estado is EstadoPedido.CONFIRMADO
    with pytest.raises(ErrorDominio, match="CREADO"):
        servicio.agregar_producto(pedido.id, producto.id, 1)
    assert servicio.obtener_producto(producto.id).stock == 4


def test_no_confirma_pedido_vacio(base_pruebas) -> None:
    servicio, cliente, _ = preparar_tienda()
    pedido = servicio.crear_pedido(cliente.id)

    with pytest.raises(ErrorDominio, match="sin productos"):
        servicio.confirmar_pedido(pedido.id)


def test_cancelar_repone_stock_una_sola_vez(base_pruebas) -> None:
    servicio, cliente, producto = preparar_tienda()
    pedido = servicio.crear_pedido(cliente.id)
    servicio.agregar_producto(pedido.id, producto.id, 3)

    cancelado = servicio.cancelar_pedido(pedido.id)

    assert cancelado.estado is EstadoPedido.CANCELADO
    assert servicio.obtener_producto(producto.id).stock == 5
    with pytest.raises(ErrorDominio, match="cancelado"):
        servicio.cancelar_pedido(pedido.id)
    assert servicio.obtener_producto(producto.id).stock == 5


@pytest.mark.parametrize("confirmar", [False, True])
def test_eliminar_pedido_activo_repone_stock(base_pruebas, confirmar: bool) -> None:
    servicio, cliente, producto = preparar_tienda()
    pedido = servicio.crear_pedido(cliente.id)
    servicio.agregar_producto(pedido.id, producto.id, 4)
    if confirmar:
        servicio.confirmar_pedido(pedido.id)

    servicio.eliminar_pedido(pedido.id)

    assert servicio.obtener_producto(producto.id).stock == 5
    with pytest.raises(ErrorDominio, match="pedido"):
        servicio.obtener_pedido(pedido.id)


def test_eliminar_pedido_cancelado_no_duplica_stock(base_pruebas) -> None:
    servicio, cliente, producto = preparar_tienda()
    pedido = servicio.crear_pedido(cliente.id)
    servicio.agregar_producto(pedido.id, producto.id, 2)
    servicio.cancelar_pedido(pedido.id)

    servicio.eliminar_pedido(pedido.id)

    assert servicio.obtener_producto(producto.id).stock == 5


def test_cancelaciones_concurrentes_devuelven_stock_una_vez(tmp_path) -> None:
    base = SqliteDatabase(
        tmp_path / "concurrencia.db",
        pragmas={"foreign_keys": 1, "journal_mode": "wal"},
        check_same_thread=False,
        timeout=5,
    )
    configurar_base_datos(base)
    base.connect()
    crear_tablas()
    servicio, cliente, producto = preparar_tienda()
    pedido = servicio.crear_pedido(cliente.id)
    servicio.agregar_producto(pedido.id, producto.id, 3)
    base.close()

    def cancelar() -> str:
        try:
            TiendaServicio().cancelar_pedido(pedido.id)
            return "cancelado"
        except ErrorDominio:
            return "rechazado"

    with ThreadPoolExecutor(max_workers=2) as ejecutor:
        resultados = list(ejecutor.map(lambda _: cancelar(), range(2)))

    assert sorted(resultados) == ["cancelado", "rechazado"]
    assert TiendaServicio().obtener_producto(producto.id).stock == 5
    base.close()
