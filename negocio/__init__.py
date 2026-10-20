"""Capa de reglas de negocio de la tienda en línea."""

from typing import TYPE_CHECKING

from negocio.entidades import (
    Cliente,
    DetallePedido,
    ErrorDominio,
    EstadoPedido,
    Pedido,
    Producto,
)
if TYPE_CHECKING:
    from negocio.servicios import TiendaServicio

__all__ = [
    "Cliente",
    "DetallePedido",
    "ErrorDominio",
    "EstadoPedido",
    "Pedido",
    "Producto",
    "TiendaServicio",
]


def __getattr__(nombre: str):
    if nombre == "TiendaServicio":
        from negocio.servicios import TiendaServicio

        return TiendaServicio
    raise AttributeError(f"El módulo {__name__!r} no contiene {nombre!r}.")
