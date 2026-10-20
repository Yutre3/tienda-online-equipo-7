"""Formato tabular para los resultados de consola."""

from collections.abc import Sequence

from prettytable import PrettyTable

from negocio.entidades import Cliente, Pedido, Producto


def formatear_dinero(centavos: int) -> str:
    pesos = centavos // 100
    return "$" + f"{pesos:,}".replace(",", ".")


def tabla_clientes(clientes: Sequence[Cliente]) -> str:
    if not clientes:
        return "Sin clientes registrados."
    tabla = PrettyTable(["ID", "Nombre", "Correo"])
    tabla.align = "l"
    for cliente in clientes:
        tabla.add_row([cliente.id, cliente.nombre, cliente.correo])
    return tabla.get_string()


def tabla_productos(productos: Sequence[Producto]) -> str:
    if not productos:
        return "Sin productos registrados."
    tabla = PrettyTable(["ID", "SKU", "Nombre", "Precio", "Stock"])
    tabla.align = "l"
    for producto in productos:
        tabla.add_row([
            producto.id,
            producto.sku,
            producto.nombre,
            formatear_dinero(producto.precio_centavos),
            producto.stock,
        ])
    return tabla.get_string()


def tabla_pedidos(pedidos: Sequence[Pedido]) -> str:
    if not pedidos:
        return "Sin pedidos registrados."
    tabla = PrettyTable(["ID", "Cliente", "Estado", "Total", "Fecha"])
    tabla.align = "l"
    for pedido in pedidos:
        fecha = pedido.creado_en.strftime("%d-%m-%Y %H:%M") if pedido.creado_en else "-"
        tabla.add_row([
            pedido.id,
            pedido.cliente.nombre,
            pedido.estado.value,
            formatear_dinero(pedido.total_centavos),
            fecha,
        ])
    return tabla.get_string()


def tabla_detalles(pedido: Pedido) -> str:
    if not pedido.detalles:
        return "El pedido no contiene productos."
    tabla = PrettyTable(["Producto", "Cantidad", "Precio", "Subtotal"])
    tabla.align = "l"
    for detalle in pedido.detalles:
        tabla.add_row([
            f"{detalle.producto.sku} - {detalle.producto.nombre}",
            detalle.cantidad,
            formatear_dinero(detalle.precio_unitario_centavos),
            formatear_dinero(detalle.subtotal_centavos),
        ])
    tabla.add_row(["TOTAL", "", "", formatear_dinero(pedido.total_centavos)])
    return tabla.get_string()
