"""Menú de consola de la tienda en línea."""

import mysql.connector

from auxiliares.info_app import NOMBRE_APLICACION
from auxiliares.opciones_menu import OPCIONES_MENU
from datos.models import Cliente, Producto, TiendaRepositorio
from negocio import TiendaServicio


def _entero(mensaje: str, minimo: int = 1) -> int:
    valor = int(input(mensaje).strip())
    if valor < minimo:
        raise ValueError(f"El valor debe ser mayor o igual que {minimo}.")
    return valor


def _registrar_cliente(servicio: TiendaServicio) -> None:
    cliente = servicio.registrar_cliente(Cliente(input("Nombre: "), input("Correo: ")))
    print(f"Cliente registrado con identificador {cliente.id}.")


def _registrar_producto(servicio: TiendaServicio) -> None:
    producto = Producto(input("Nombre: "), input("Descripción: "),
                        _entero("Precio en pesos: ") * 100,
                        _entero("Stock inicial: ", 0))
    servicio.registrar_producto(producto)
    print(f"Producto registrado con identificador {producto.id}.")


def _crear_pedido(servicio: TiendaServicio, repositorio: TiendaRepositorio) -> None:
    cliente = repositorio.obtener_cliente(_entero("Identificador del cliente: "))
    pedido = servicio.crear_pedido(cliente)
    print(f"Pedido creado con identificador {pedido.id}.")


def _agregar_producto(servicio: TiendaServicio,
                      repositorio: TiendaRepositorio) -> None:
    pedido = repositorio.obtener_pedido(_entero("Identificador del pedido: "))
    producto = repositorio.obtener_producto(_entero("Identificador del producto: "))
    detalle = servicio.agregar_producto(pedido, producto, _entero("Cantidad: "))
    print(f"Producto agregado. Subtotal: ${detalle.subtotal_centavos // 100}; "
          f"total del pedido: ${pedido.total_centavos // 100}.")


def _mostrar_datos(repositorio: TiendaRepositorio) -> None:
    clientes, productos, pedidos = repositorio.resumen()
    print("\nCLIENTES")
    for fila in clientes:
        print(f"{fila['id']}: {fila['nombre']} <{fila['correo']}>")
    if not clientes:
        print("Sin registros.")
    print("\nPRODUCTOS")
    for fila in productos:
        print(f"{fila['id']}: {fila['nombre']} - "
              f"${fila['precio_centavos'] // 100} - stock {fila['stock']}")
    if not productos:
        print("Sin registros.")
    print("\nPEDIDOS")
    for fila in pedidos:
        print(f"{fila['id']}: {fila['cliente']} - {fila['estado']} - "
              f"${fila['total_centavos'] // 100} - {fila['creado_en']}")
    if not pedidos:
        print("Sin registros.")


def menu_principal(servicio: TiendaServicio,
                   repositorio: TiendaRepositorio) -> None:
    acciones = {
        "1": lambda: _registrar_cliente(servicio),
        "2": lambda: _registrar_producto(servicio),
        "3": lambda: _crear_pedido(servicio, repositorio),
        "4": lambda: _agregar_producto(servicio, repositorio),
        "5": lambda: _mostrar_datos(repositorio),
    }
    while True:
        print(f"\n{NOMBRE_APLICACION.upper()}\n{'=' * len(NOMBRE_APLICACION)}")
        for clave, descripcion in OPCIONES_MENU.items():
            print(f"[{clave}] {descripcion}")
        opcion = input("Ingrese una opción [0-5]: ").strip()
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
