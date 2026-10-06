"""Conversión entre registros de la base y modelos del dominio.

Este módulo ocupa dentro de la capa ``datos`` el lugar de ``models.py`` que se
observa en el proyecto del profesor. Las clases del dominio permanecen en
``negocio`` para no mezclar las reglas de la tienda con las consultas SQL.
"""

from typing import Any

from negocio.entidades import Cliente, Pedido, Producto


Fila = dict[str, Any]


def cliente_desde_fila(fila: Fila) -> Cliente:
    return Cliente(fila["nombre"], fila["correo"], fila["id"])


def producto_desde_fila(fila: Fila) -> Producto:
    return Producto(
        fila["nombre"],
        fila["descripcion"],
        fila["precio_centavos"],
        fila["stock"],
        fila["id"],
    )


def pedido_desde_fila(fila: Fila) -> Pedido:
    cliente = Cliente(fila["nombre"], fila["correo"], fila["cliente_id"])
    return Pedido(cliente, fila["estado"], fila["total_centavos"], fila["id"])
