"""Reglas de negocio de la tienda en línea."""

from datos.models import Cliente, DetallePedido, Pedido, Producto, TiendaRepositorio


class TiendaServicio:
    def __init__(self, repositorio: TiendaRepositorio) -> None:
        self._repositorio = repositorio

    def registrar_cliente(self, cliente: Cliente) -> Cliente:
        self._repositorio.guardar_cliente(cliente)
        return cliente

    def registrar_producto(self, producto: Producto) -> Producto:
        self._repositorio.guardar_producto(producto)
        return producto

    def crear_pedido(self, cliente: Cliente) -> Pedido:
        pedido = Pedido(cliente)
        self._repositorio.guardar_pedido(pedido)
        return pedido

    def agregar_producto(self, pedido: Pedido, producto: Producto,
                         cantidad: int) -> DetallePedido:
        detalle = DetallePedido(producto, cantidad)
        self._repositorio.guardar_detalle(pedido, detalle)
        producto.descontar_stock(cantidad)
        pedido.agregar_detalle(detalle)
        return detalle
