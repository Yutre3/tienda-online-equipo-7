import pytest

from negocio.entidades import (
    Cliente,
    DetallePedido,
    ErrorDominio,
    EstadoPedido,
    Pedido,
    Producto,
)


def test_cliente_normaliza_nombre_y_correo() -> None:
    cliente = Cliente("  Ana Pérez  ", "  ANA@EJEMPLO.CL ")

    assert cliente.nombre == "Ana Pérez"
    assert cliente.correo == "ana@ejemplo.cl"


@pytest.mark.parametrize("correo", ["", "sin-arroba.cl", "a@", "@dominio.cl"])
def test_cliente_rechaza_correo_invalido(correo: str) -> None:
    with pytest.raises(ErrorDominio, match="correo"):
        Cliente("Ana", correo)


def test_producto_normaliza_sku_y_valida_valores() -> None:
    producto = Producto("  sku-001 ", " Teclado ", " Mecánico ", 2599000, 4)

    assert producto.sku == "SKU-001"
    assert producto.nombre == "Teclado"
    assert producto.descripcion == "Mecánico"
    assert producto.precio_centavos == 2599000
    assert producto.stock == 4


@pytest.mark.parametrize(
    ("precio", "stock"),
    [(0, 1), (-1, 1), (100, -1), (True, 1), (100, False)],
)
def test_producto_rechaza_precio_o_stock_invalidos(precio: int, stock: int) -> None:
    with pytest.raises(ErrorDominio):
        Producto("SKU-1", "Producto", "", precio, stock)


def test_detalle_calcula_subtotal_literal() -> None:
    producto = Producto("SKU-1", "Mouse", "", 1299000, 10, identificador=5)
    detalle = DetallePedido(producto, 3)

    assert detalle.subtotal_centavos == 3897000


@pytest.mark.parametrize("cantidad", [0, -1, True])
def test_detalle_rechaza_cantidad_invalida(cantidad: int) -> None:
    producto = Producto("SKU-1", "Mouse", "", 100, 10)

    with pytest.raises(ErrorDominio, match="cantidad"):
        DetallePedido(producto, cantidad)


def test_pedido_suma_detalles_y_actualiza_cantidad_repetida() -> None:
    cliente = Cliente("Ana", "ana@ejemplo.cl", identificador=1)
    producto = Producto("SKU-1", "Mouse", "", 1500, 10, identificador=2)
    pedido = Pedido(cliente)

    pedido.agregar_detalle(DetallePedido(producto, 2))
    pedido.agregar_detalle(DetallePedido(producto, 1))

    assert len(pedido.detalles) == 1
    assert pedido.detalles[0].cantidad == 3
    assert pedido.total_centavos == 4500


def test_pedido_confirmado_no_admite_modificaciones() -> None:
    cliente = Cliente("Ana", "ana@ejemplo.cl", identificador=1)
    producto = Producto("SKU-1", "Mouse", "", 1500, 10, identificador=2)
    pedido = Pedido(cliente)
    pedido.agregar_detalle(DetallePedido(producto, 1))
    pedido.cambiar_estado(EstadoPedido.CONFIRMADO)

    with pytest.raises(ErrorDominio, match="CREADO"):
        pedido.agregar_detalle(DetallePedido(producto, 1))


def test_pedido_no_se_confirma_sin_productos() -> None:
    pedido = Pedido(Cliente("Ana", "ana@ejemplo.cl", identificador=1))

    with pytest.raises(ErrorDominio, match="sin productos"):
        pedido.cambiar_estado(EstadoPedido.CONFIRMADO)
