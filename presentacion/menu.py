"""Menú de consola completo de la tienda en línea."""

from collections.abc import Callable

from peewee import PeeweeException

from auxiliares.info_app import NOMBRE_APLICACION, VERSION_APLICACION
from auxiliares.opciones_menu import OPCIONES_MENU
from negocio import Cliente, ErrorDominio, Producto, TiendaServicio
from presentacion.entradas import Entrada, Salida, solicitar_entero, solicitar_texto
from presentacion.tablas import tabla_clientes, tabla_detalles, tabla_pedidos, tabla_productos


def _mostrar_opciones(titulo: str, opciones: dict[str, str], salida: Salida) -> None:
    salida(f"\n{titulo}")
    salida("=" * len(titulo))
    for clave, descripcion in opciones.items():
        salida(f"[{clave}] {descripcion}")


def _ejecutar(
    accion: Callable[[], None],
    salida: Salida,
) -> None:
    try:
        accion()
    except (ErrorDominio, PeeweeException) as error:
        salida(f"No se pudo completar la operación: {error}")


def _menu_clientes(servicio: TiendaServicio, entrada: Entrada, salida: Salida) -> None:
    opciones = {"1": "Listar", "2": "Registrar", "3": "Editar", "4": "Eliminar", "0": "Volver"}

    def registrar() -> None:
        cliente = servicio.registrar_cliente(Cliente(
            solicitar_texto("Nombre: ", entrada=entrada, salida=salida),
            solicitar_texto("Correo: ", entrada=entrada, salida=salida),
        ))
        salida(f"Cliente registrado con ID {cliente.id}.")

    def editar() -> None:
        cliente = servicio.obtener_cliente(solicitar_entero("ID: ", minimo=1, entrada=entrada, salida=salida))
        cliente.nombre = solicitar_texto("Nuevo nombre: ", entrada=entrada, salida=salida)
        cliente.correo = solicitar_texto("Nuevo correo: ", entrada=entrada, salida=salida)
        servicio.actualizar_cliente(cliente)
        salida("Cliente actualizado.")

    def eliminar() -> None:
        servicio.eliminar_cliente(solicitar_entero("ID: ", minimo=1, entrada=entrada, salida=salida))
        salida("Cliente eliminado.")

    acciones: dict[str, Callable[[], None]] = {
        "1": lambda: salida(tabla_clientes(servicio.listar_clientes())),
        "2": registrar,
        "3": editar,
        "4": eliminar,
    }
    _bucle_submenu("CLIENTES", opciones, acciones, entrada, salida)


def _menu_productos(servicio: TiendaServicio, entrada: Entrada, salida: Salida) -> None:
    opciones = {"1": "Listar", "2": "Registrar", "3": "Editar", "4": "Eliminar", "0": "Volver"}

    def leer_producto(actual: Producto | None = None) -> Producto:
        identificador = actual.id if actual else None
        return Producto(
            solicitar_texto("SKU: ", entrada=entrada, salida=salida),
            solicitar_texto("Nombre: ", entrada=entrada, salida=salida),
            entrada("Descripción: ").strip(),
            solicitar_entero("Precio en pesos: ", minimo=1, entrada=entrada, salida=salida) * 100,
            solicitar_entero("Stock: ", minimo=0, entrada=entrada, salida=salida),
            identificador,
            actual.creado_en if actual else None,
        )

    def registrar() -> None:
        producto = servicio.registrar_producto(leer_producto())
        salida(f"Producto registrado con ID {producto.id}.")

    def editar() -> None:
        actual = servicio.obtener_producto(solicitar_entero("ID: ", minimo=1, entrada=entrada, salida=salida))
        servicio.actualizar_producto(leer_producto(actual))
        salida("Producto actualizado.")

    def eliminar() -> None:
        servicio.eliminar_producto(solicitar_entero("ID: ", minimo=1, entrada=entrada, salida=salida))
        salida("Producto eliminado.")

    acciones: dict[str, Callable[[], None]] = {
        "1": lambda: salida(tabla_productos(servicio.listar_productos())),
        "2": registrar,
        "3": editar,
        "4": eliminar,
    }
    _bucle_submenu("PRODUCTOS", opciones, acciones, entrada, salida)


def _menu_pedidos(servicio: TiendaServicio, entrada: Entrada, salida: Salida) -> None:
    opciones = {
        "1": "Listar", "2": "Ver detalle", "3": "Crear", "4": "Agregar producto",
        "5": "Quitar producto", "6": "Confirmar", "7": "Cancelar", "8": "Eliminar", "0": "Volver",
    }

    def id_pedido() -> int:
        return solicitar_entero("ID del pedido: ", minimo=1, entrada=entrada, salida=salida)

    def crear() -> None:
        pedido = servicio.crear_pedido(solicitar_entero("ID del cliente: ", minimo=1, entrada=entrada, salida=salida))
        salida(f"Pedido creado con ID {pedido.id}.")

    def agregar() -> None:
        pedido = servicio.agregar_producto(
            id_pedido(),
            solicitar_entero("ID del producto: ", minimo=1, entrada=entrada, salida=salida),
            solicitar_entero("Cantidad: ", minimo=1, entrada=entrada, salida=salida),
        )
        salida(tabla_detalles(pedido))

    def quitar() -> None:
        pedido = servicio.quitar_producto(
            id_pedido(),
            solicitar_entero("ID del producto: ", minimo=1, entrada=entrada, salida=salida),
        )
        salida(tabla_detalles(pedido))

    acciones: dict[str, Callable[[], None]] = {
        "1": lambda: salida(tabla_pedidos(servicio.listar_pedidos())),
        "2": lambda: salida(tabla_detalles(servicio.obtener_pedido(id_pedido()))),
        "3": crear,
        "4": agregar,
        "5": quitar,
        "6": lambda: salida(f"Pedido {servicio.confirmar_pedido(id_pedido()).id} confirmado."),
        "7": lambda: salida(f"Pedido {servicio.cancelar_pedido(id_pedido()).id} cancelado."),
        "8": lambda: (servicio.eliminar_pedido(id_pedido()), salida("Pedido eliminado.")),
    }
    _bucle_submenu("PEDIDOS", opciones, acciones, entrada, salida)


def _bucle_submenu(
    titulo: str,
    opciones: dict[str, str],
    acciones: dict[str, Callable[[], None]],
    entrada: Entrada,
    salida: Salida,
) -> None:
    while True:
        _mostrar_opciones(titulo, opciones, salida)
        opcion = entrada("Seleccione una opción: ").strip()
        if opcion == "0":
            return
        accion = acciones.get(opcion)
        if accion is None:
            salida("Opción inválida.")
        else:
            _ejecutar(accion, salida)


def menu_principal(
    servicio: TiendaServicio,
    *,
    entrada: Entrada = input,
    salida: Salida = print,
) -> None:
    acciones: dict[str, Callable[[], None]] = {
        "1": lambda: _menu_clientes(servicio, entrada, salida),
        "2": lambda: _menu_productos(servicio, entrada, salida),
        "3": lambda: _menu_pedidos(servicio, entrada, salida),
        "4": lambda: (
            salida(tabla_clientes(servicio.listar_clientes())),
            salida(tabla_productos(servicio.listar_productos())),
            salida(tabla_pedidos(servicio.listar_pedidos())),
        ),
    }
    while True:
        _mostrar_opciones(f"{NOMBRE_APLICACION} v{VERSION_APLICACION}", OPCIONES_MENU, salida)
        opcion = entrada("Seleccione una opción: ").strip()
        if opcion == "0":
            salida("Programa finalizado.")
            return
        accion = acciones.get(opcion)
        if accion is None:
            salida("Opción inválida.")
        else:
            _ejecutar(accion, salida)
