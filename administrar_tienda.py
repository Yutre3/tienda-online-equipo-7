from __future__ import annotations

import mysql.connector

from base_datos import BaseDeDatos
from modelos import Cliente, Pedido, Producto
from servicios import TiendaServicio


def pedir_entero(mensaje: str, minimo: int = 1) -> int:
    valor = int(input(mensaje).strip())
    if valor < minimo:
        raise ValueError(f"El valor debe ser mayor o igual que {minimo}.")
    return valor


def obtener_cliente(base_datos: BaseDeDatos, identificador: int) -> Cliente:
    conexion = base_datos.conectar()
    try:
        with conexion.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT id, nombre, correo FROM clientes WHERE id = %s",
                (identificador,),
            )
            fila = cursor.fetchone()
    finally:
        conexion.close()
    if fila is None:
        raise ValueError("No existe un cliente con ese identificador.")
    return Cliente(fila["nombre"], fila["correo"], fila["id"])


def obtener_producto(base_datos: BaseDeDatos, identificador: int) -> Producto:
    conexion = base_datos.conectar()
    try:
        with conexion.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT id, nombre, descripcion, precio_centavos, stock
                FROM productos WHERE id = %s
                """,
                (identificador,),
            )
            fila = cursor.fetchone()
    finally:
        conexion.close()
    if fila is None:
        raise ValueError("No existe un producto con ese identificador.")
    return Producto(
        fila["nombre"],
        fila["descripcion"],
        fila["precio_centavos"],
        fila["stock"],
        fila["id"],
    )


def obtener_pedido(base_datos: BaseDeDatos, identificador: int) -> Pedido:
    conexion = base_datos.conectar()
    try:
        with conexion.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT p.id, p.estado, p.total_centavos,
                       c.id AS cliente_id, c.nombre, c.correo
                FROM pedidos p
                JOIN clientes c ON c.id = p.cliente_id
                WHERE p.id = %s
                """,
                (identificador,),
            )
            fila = cursor.fetchone()
    finally:
        conexion.close()
    if fila is None:
        raise ValueError("No existe un pedido con ese identificador.")
    cliente = Cliente(
        fila["nombre"], fila["correo"], fila["cliente_id"]
    )
    return Pedido(
        cliente,
        fila["estado"],
        fila["total_centavos"],
        fila["id"],
    )


def registrar_cliente(servicio: TiendaServicio) -> None:
    cliente = Cliente(input("Nombre: "), input("Correo: "))
    servicio.registrar_cliente(cliente)
    print(f"Cliente registrado con identificador {cliente.id}.")


def registrar_producto(servicio: TiendaServicio) -> None:
    producto = Producto(
        input("Nombre: "),
        input("Descripción: "),
        pedir_entero("Precio en pesos: ") * 100,
        pedir_entero("Stock inicial: ", minimo=0),
    )
    servicio.registrar_producto(producto)
    print(f"Producto registrado con identificador {producto.id}.")


def crear_pedido(base_datos: BaseDeDatos, servicio: TiendaServicio) -> None:
    cliente = obtener_cliente(base_datos, pedir_entero("Identificador del cliente: "))
    pedido = servicio.crear_pedido(cliente)
    print(f"Pedido creado con identificador {pedido.id}.")


def agregar_producto(
    base_datos: BaseDeDatos, servicio: TiendaServicio
) -> None:
    pedido = obtener_pedido(base_datos, pedir_entero("Identificador del pedido: "))
    producto = obtener_producto(
        base_datos, pedir_entero("Identificador del producto: ")
    )
    cantidad = pedir_entero("Cantidad: ")
    detalle = servicio.agregar_producto(pedido, producto, cantidad)
    print(
        "Producto agregado. "
        f"Subtotal: ${detalle.subtotal_centavos // 100}; "
        f"total del pedido: ${pedido.total_centavos // 100}."
    )


def listar(base_datos: BaseDeDatos) -> None:
    conexion = base_datos.conectar()
    try:
        with conexion.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id, nombre, correo FROM clientes ORDER BY id")
            clientes = cursor.fetchall()
            cursor.execute(
                """
                SELECT id, nombre, precio_centavos, stock
                FROM productos ORDER BY id
                """
            )
            productos = cursor.fetchall()
            cursor.execute(
                """
                SELECT p.id, c.nombre AS cliente, p.estado,
                       p.total_centavos, p.creado_en
                FROM pedidos p
                JOIN clientes c ON c.id = p.cliente_id
                ORDER BY p.id
                """
            )
            pedidos = cursor.fetchall()
    finally:
        conexion.close()

    print("\nCLIENTES")
    for fila in clientes:
        print(f"{fila['id']}: {fila['nombre']} <{fila['correo']}>")
    if not clientes:
        print("Sin registros.")

    print("\nPRODUCTOS")
    for fila in productos:
        print(
            f"{fila['id']}: {fila['nombre']} - "
            f"${fila['precio_centavos'] // 100} - stock {fila['stock']}"
        )
    if not productos:
        print("Sin registros.")

    print("\nPEDIDOS")
    for fila in pedidos:
        print(
            f"{fila['id']}: {fila['cliente']} - {fila['estado']} - "
            f"${fila['total_centavos'] // 100} - {fila['creado_en']}"
        )
    if not pedidos:
        print("Sin registros.")


def main() -> None:
    base_datos = BaseDeDatos()
    base_datos.inicializar()
    servicio = TiendaServicio(base_datos)
    acciones = {
        "1": lambda: registrar_cliente(servicio),
        "2": lambda: registrar_producto(servicio),
        "3": lambda: crear_pedido(base_datos, servicio),
        "4": lambda: agregar_producto(base_datos, servicio),
        "5": lambda: listar(base_datos),
    }

    while True:
        print(
            "\nTIENDA EN LÍNEA\n"
            "1. Registrar cliente\n"
            "2. Registrar producto\n"
            "3. Crear pedido\n"
            "4. Agregar producto a un pedido\n"
            "5. Mostrar datos\n"
            "0. Salir"
        )
        opcion = input("Opción: ").strip()
        if opcion == "0":
            print("Programa finalizado.")
            return
        accion = acciones.get(opcion)
        if accion is None:
            print("Opción inválida.")
            continue
        try:
            accion()
        except (ValueError, TypeError, mysql.connector.Error) as error:
            print(f"No se pudo completar la operación: {error}")


if __name__ == "__main__":
    main()
