"""Compatibilidad con el nombre usado por versiones anteriores del proyecto."""

from datos.modelos import (
    ClienteModelo,
    DetallePedidoModelo,
    PedidoModelo,
    ProductoModelo,
)
from datos.repositorios import (
    RepositorioClientes,
    RepositorioPedidos,
    RepositorioProductos,
)

__all__ = [
    "ClienteModelo",
    "DetallePedidoModelo",
    "PedidoModelo",
    "ProductoModelo",
    "RepositorioClientes",
    "RepositorioPedidos",
    "RepositorioProductos",
]
