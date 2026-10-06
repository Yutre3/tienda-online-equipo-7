"""Casos de uso de la tienda."""

from datos.repositorios import TiendaRepositorio
from negocio.entidades import Cliente, DetallePedido, Pedido, Producto


class TiendaServicio:
    def __init__(self, repositorio: TiendaRepositorio) -> None:
        self._repositorio = repositorio

    def registrar_cliente(self, cliente: Cliente) -> Cliente:
        if cliente.id is not None:
            raise ValueError("El cliente ya está registrado.")
        self._repositorio.guardar_cliente(cliente)
        return cliente

    def registrar_producto(self, producto: Producto) -> Producto:
        if producto.id is not None:
            raise ValueError("El producto ya está registrado.")
        self._repositorio.guardar_producto(producto)
        return producto

    def crear_pedido(self, cliente: Cliente) -> Pedido:
        if cliente.id is None:
            raise ValueError("El cliente debe estar registrado antes de crear un pedido.")
        pedido = Pedido(cliente)
        self._repositorio.guardar_pedido(pedido)
        return pedido

    def agregar_producto(self, pedido: Pedido, producto: Producto,
                         cantidad: int) -> DetallePedido:
        if pedido.id is None or producto.id is None:
            raise ValueError("El pedido y el producto deben estar registrados.")
        detalle = DetallePedido(producto, cantidad)
        self._repositorio.guardar_detalle(pedido, detalle)
        producto.descontar_stock(cantidad)
        pedido.agregar_detalle(detalle)
        return detalle
