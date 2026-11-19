import subprocess
import sys

import pytest
from peewee import SqliteDatabase

from datos.conexion import configurar_base_datos, crear_tablas
from datos.repositorios import (
    RepositorioClientes,
    RepositorioPedidos,
    RepositorioProductos,
)
from negocio.entidades import Cliente, DetallePedido, ErrorDominio, Pedido, Producto


def test_repositorios_se_pueden_importar_antes_que_negocio() -> None:
    resultado = subprocess.run(
        [sys.executable, "-c", "import datos.repositorios"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert resultado.returncode == 0, resultado.stderr


def test_crear_tablas_migra_productos_anteriores_sin_sku() -> None:
    base = SqliteDatabase(":memory:", pragmas={"foreign_keys": 1})
    configurar_base_datos(base)
    base.connect()
    base.execute_sql(
        """
        CREATE TABLE productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(150) NOT NULL,
            descripcion TEXT NOT NULL,
            precio_centavos INTEGER NOT NULL,
            stock INTEGER NOT NULL,
            creado_en DATETIME NOT NULL,
            actualizado_en DATETIME NOT NULL
        )
        """
    )
    base.execute_sql(
        """
        INSERT INTO productos
            (nombre, descripcion, precio_centavos, stock, creado_en, actualizado_en)
        VALUES ('Producto anterior', '', 150000, 7, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """
    )

    crear_tablas()

    producto = RepositorioProductos().obtener(1)
    assert producto.sku == "LEGACY-000001"
    assert producto.nombre == "Producto anterior"
    assert producto.stock == 7
    base.close()


def test_crud_de_clientes_y_correo_unico(base_pruebas) -> None:
    repositorio = RepositorioClientes()
    cliente = repositorio.crear(Cliente("Ana", "ana@ejemplo.cl"))

    assert cliente.id == 1
    assert repositorio.obtener(1).correo == "ana@ejemplo.cl"
    cliente.nombre = "Ana María"
    repositorio.actualizar(cliente)
    assert [actual.nombre for actual in repositorio.listar()] == ["Ana María"]

    with pytest.raises(ErrorDominio, match="correo"):
        repositorio.crear(Cliente("Otra", "ana@ejemplo.cl"))

    repositorio.eliminar(1)
    assert repositorio.listar() == []


def test_crud_de_productos_y_sku_unico(base_pruebas) -> None:
    repositorio = RepositorioProductos()
    producto = repositorio.crear(Producto("TEC-1", "Teclado", "Mecánico", 3999000, 5))

    assert producto.id == 1
    producto.stock = 8
    repositorio.actualizar(producto)
    guardado = repositorio.obtener(1)
    assert (guardado.sku, guardado.stock, guardado.precio_centavos) == (
        "TEC-1",
        8,
        3999000,
    )

    with pytest.raises(ErrorDominio, match="SKU"):
        repositorio.crear(Producto("tec-1", "Otro", "", 100, 1))

    repositorio.eliminar(1)
    assert repositorio.listar() == []


def test_pedido_con_detalles_se_convierte_en_entidad_completa(base_pruebas) -> None:
    clientes = RepositorioClientes()
    productos = RepositorioProductos()
    pedidos = RepositorioPedidos()
    cliente = clientes.crear(Cliente("Ana", "ana@ejemplo.cl"))
    mouse = productos.crear(Producto("MOU-1", "Mouse", "", 1299000, 10))
    pedido = pedidos.crear(Pedido(cliente))

    pedidos.guardar_detalle(pedido.id, DetallePedido(mouse, 2))
    recuperado = pedidos.obtener(pedido.id)

    assert recuperado.cliente.id == cliente.id
    assert len(recuperado.detalles) == 1
    assert recuperado.detalles[0].producto.sku == "MOU-1"
    assert recuperado.total_centavos == 2598000
    assert pedidos.listar()[0].total_centavos == 2598000


def test_guardar_producto_repetido_acumula_cantidad(base_pruebas) -> None:
    clientes = RepositorioClientes()
    productos = RepositorioProductos()
    pedidos = RepositorioPedidos()
    cliente = clientes.crear(Cliente("Ana", "ana@ejemplo.cl"))
    producto = productos.crear(Producto("MOU-1", "Mouse", "", 500, 10))
    pedido = pedidos.crear(Pedido(cliente))

    pedidos.guardar_detalle(pedido.id, DetallePedido(producto, 2))
    pedidos.guardar_detalle(pedido.id, DetallePedido(producto, 3))

    recuperado = pedidos.obtener(pedido.id)
    assert len(recuperado.detalles) == 1
    assert recuperado.detalles[0].cantidad == 5
    assert recuperado.total_centavos == 2500


def test_obtener_identificador_inexistente_informa_error(base_pruebas) -> None:
    with pytest.raises(ErrorDominio, match="cliente"):
        RepositorioClientes().obtener(999)
    with pytest.raises(ErrorDominio, match="producto"):
        RepositorioProductos().obtener(999)
    with pytest.raises(ErrorDominio, match="pedido"):
        RepositorioPedidos().obtener(999)


def test_no_elimina_cliente_relacionado_con_pedido(base_pruebas) -> None:
    clientes = RepositorioClientes()
    cliente = clientes.crear(Cliente("Ana", "ana@ejemplo.cl"))
    RepositorioPedidos().crear(Pedido(cliente))

    with pytest.raises(ErrorDominio, match="pedidos"):
        clientes.eliminar(cliente.id)
