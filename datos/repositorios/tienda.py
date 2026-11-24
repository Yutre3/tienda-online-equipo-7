"""Adaptadores compatibles para los repositorios funcionales de la tienda."""

from datos.repositorio import clientes, pedidos, productos
from negocio.entidades import Cliente, DetallePedido, EstadoPedido, Pedido, Producto


class RepositorioClientes:
    def crear(self, cliente: Cliente) -> Cliente:
        return clientes.guardar_cliente(cliente)

    def obtener(self, identificador: int) -> Cliente:
        return clientes.obtener_cliente(identificador)

    def listar(self) -> list[Cliente]:
        return clientes.listar_clientes()

    def actualizar(self, cliente: Cliente) -> Cliente:
        return clientes.modificar_cliente(cliente)

    def eliminar(self, identificador: int) -> None:
        clientes.eliminar_cliente(identificador)


class RepositorioProductos:
    def crear(self, producto: Producto) -> Producto:
        return productos.guardar_producto(producto)

    def obtener(self, identificador: int) -> Producto:
        return productos.obtener_producto(identificador)

    def listar(self) -> list[Producto]:
        return productos.listar_productos()

    def actualizar(self, producto: Producto) -> Producto:
        return productos.modificar_producto(producto)

    def eliminar(self, identificador: int) -> None:
        productos.eliminar_producto(identificador)

    def descontar_stock(self, identificador: int, cantidad: int) -> None:
        productos.descontar_stock(identificador, cantidad)

    def reponer_stock(self, identificador: int, cantidad: int) -> None:
        productos.reponer_stock(identificador, cantidad)


class RepositorioPedidos:
    def crear(self, pedido: Pedido) -> Pedido:
        return pedidos.guardar_pedido(pedido)

    def obtener(self, identificador: int) -> Pedido:
        return pedidos.obtener_pedido(identificador)

    def obtener_para_actualizar(self, identificador: int) -> Pedido:
        return pedidos.obtener_pedido_para_actualizar(identificador)

    def listar(self) -> list[Pedido]:
        return pedidos.listar_pedidos()

    def guardar_detalle(
        self, pedido_id: int | None, detalle: DetallePedido
    ) -> DetallePedido:
        return pedidos.guardar_detalle(pedido_id, detalle)

    def eliminar_detalle(
        self, pedido_id: int, producto_id: int
    ) -> DetallePedido:
        return pedidos.eliminar_detalle(pedido_id, producto_id)

    def cambiar_estado(self, pedido_id: int, estado: EstadoPedido) -> None:
        pedidos.cambiar_estado_pedido(pedido_id, estado)

    def eliminar(self, pedido_id: int) -> None:
        pedidos.eliminar_pedido(pedido_id)

    def recalcular_total(self, pedido_id: int) -> int:
        return pedidos.recalcular_total(pedido_id)
