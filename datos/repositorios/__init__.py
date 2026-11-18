"""Repositorios disponibles para la capa de negocio."""

from datos.repositorios.repositorio_pais import RepositorioPaises
from datos.repositorios.repositorio_usuario import RepositorioUsuarios
from datos.repositorios.tienda import (
    RepositorioClientes,
    RepositorioPedidos,
    RepositorioProductos,
)

__all__ = [
    "RepositorioClientes",
    "RepositorioPaises",
    "RepositorioPedidos",
    "RepositorioProductos",
    "RepositorioUsuarios",
]
