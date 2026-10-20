"""Repositorios disponibles para la capa de negocio."""

from datos.repositorios.tienda import (
    RepositorioClientes,
    RepositorioPedidos,
    RepositorioProductos,
)

__all__ = ["RepositorioClientes", "RepositorioPedidos", "RepositorioProductos"]
