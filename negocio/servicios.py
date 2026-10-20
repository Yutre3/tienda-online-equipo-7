"""Casos de uso y transacciones de la tienda en línea."""

from datos.conexion import transaccion_escritura
from datos.repositorios import (
    RepositorioClientes,
    RepositorioPedidos,
    RepositorioProductos,
)
from negocio.entidades import (
    Cliente,
    DetallePedido,
    ErrorDominio,
    EstadoPedido,
    Pedido,
    Producto,
)


def _id_requerido(identificador: int | None, tipo: str) -> int:
    if identificador is None:
        raise ErrorDominio(f"El {tipo} todavía no ha sido guardado.")
    return identificador


class TiendaServicio:
    """Fachada de negocio utilizada por la presentación."""

    def __init__(
        self,
        clientes: RepositorioClientes | None = None,
        productos: RepositorioProductos | None = None,
        pedidos: RepositorioPedidos | None = None,
    ) -> None:
        self._clientes = clientes or RepositorioClientes()
        self._productos = productos or RepositorioProductos()
        self._pedidos = pedidos or RepositorioPedidos()

    def registrar_cliente(self, cliente: Cliente) -> Cliente:
        return self._clientes.crear(cliente)

    def obtener_cliente(self, identificador: int) -> Cliente:
        return self._clientes.obtener(identificador)

    def listar_clientes(self) -> list[Cliente]:
        return self._clientes.listar()

    def actualizar_cliente(self, cliente: Cliente) -> Cliente:
        return self._clientes.actualizar(cliente)

    def eliminar_cliente(self, identificador: int | None) -> None:
        self._clientes.eliminar(_id_requerido(identificador, "cliente"))

    def registrar_producto(self, producto: Producto) -> Producto:
        return self._productos.crear(producto)

    def obtener_producto(self, identificador: int) -> Producto:
        return self._productos.obtener(identificador)

    def listar_productos(self) -> list[Producto]:
        return self._productos.listar()

    def actualizar_producto(self, producto: Producto) -> Producto:
        return self._productos.actualizar(producto)

    def eliminar_producto(self, identificador: int | None) -> None:
        self._productos.eliminar(_id_requerido(identificador, "producto"))

    def crear_pedido(self, cliente_id: int) -> Pedido:
        cliente = self._clientes.obtener(cliente_id)
        return self._pedidos.crear(Pedido(cliente))

    def obtener_pedido(self, identificador: int) -> Pedido:
        return self._pedidos.obtener(identificador)

    def listar_pedidos(self) -> list[Pedido]:
        return self._pedidos.listar()

    def agregar_producto(
        self, pedido_id: int, producto_id: int, cantidad: int
    ) -> Pedido:
        with transaccion_escritura():
            pedido = self._pedidos.obtener_para_actualizar(pedido_id)
            if pedido.estado is not EstadoPedido.CREADO:
                raise ErrorDominio(
                    "Solo se pueden modificar pedidos en estado CREADO."
                )
            producto = self._productos.obtener(producto_id)
            detalle = DetallePedido(producto, cantidad)
            self._productos.descontar_stock(producto_id, cantidad)
            self._pedidos.guardar_detalle(pedido_id, detalle)
        return self._pedidos.obtener(pedido_id)

    def quitar_producto(self, pedido_id: int, producto_id: int) -> Pedido:
        with transaccion_escritura():
            pedido = self._pedidos.obtener_para_actualizar(pedido_id)
            if pedido.estado is not EstadoPedido.CREADO:
                raise ErrorDominio(
                    "Solo se pueden modificar pedidos en estado CREADO."
                )
            detalle = self._pedidos.eliminar_detalle(pedido_id, producto_id)
            self._productos.reponer_stock(producto_id, detalle.cantidad)
        return self._pedidos.obtener(pedido_id)

    def confirmar_pedido(self, pedido_id: int) -> Pedido:
        with transaccion_escritura():
            pedido = self._pedidos.obtener_para_actualizar(pedido_id)
            pedido.cambiar_estado(EstadoPedido.CONFIRMADO)
            self._pedidos.cambiar_estado(pedido_id, pedido.estado)
        return self._pedidos.obtener(pedido_id)

    def cancelar_pedido(self, pedido_id: int) -> Pedido:
        with transaccion_escritura():
            pedido = self._pedidos.obtener_para_actualizar(pedido_id)
            pedido.cambiar_estado(EstadoPedido.CANCELADO)
            self._reponer_detalles(pedido)
            self._pedidos.cambiar_estado(pedido_id, pedido.estado)
        return self._pedidos.obtener(pedido_id)

    def eliminar_pedido(self, pedido_id: int) -> None:
        with transaccion_escritura():
            pedido = self._pedidos.obtener_para_actualizar(pedido_id)
            if pedido.estado is not EstadoPedido.CANCELADO:
                self._reponer_detalles(pedido)
            self._pedidos.eliminar(pedido_id)

    def _reponer_detalles(self, pedido: Pedido) -> None:
        for detalle in pedido.detalles:
            producto_id = _id_requerido(detalle.producto.id, "producto")
            self._productos.reponer_stock(producto_id, detalle.cantidad)
