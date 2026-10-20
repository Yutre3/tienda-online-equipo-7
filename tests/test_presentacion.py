from negocio import Cliente, Producto, TiendaServicio
from presentacion.entradas import solicitar_entero
from presentacion.menu import menu_principal
from presentacion.tablas import formatear_dinero, tabla_clientes, tabla_productos


def test_solicitar_entero_reintenta_hasta_recibir_valor_valido() -> None:
    respuestas = iter(["texto", "0", "3"])
    mensajes: list[str] = []

    resultado = solicitar_entero(
        "Cantidad: ",
        minimo=1,
        entrada=lambda _: next(respuestas),
        salida=mensajes.append,
    )

    assert resultado == 3
    assert mensajes == [
        "Ingrese un número entero válido.",
        "El valor debe ser mayor o igual que 1.",
    ]


def test_formatear_dinero_muestra_pesos_chilenos() -> None:
    assert formatear_dinero(1299000) == "$12.990"
    assert formatear_dinero(0) == "$0"


def test_tablas_muestran_registros_y_mensaje_vacio(base_pruebas) -> None:
    servicio = TiendaServicio()
    cliente = servicio.registrar_cliente(Cliente("Ana", "ana@ejemplo.cl"))
    producto = servicio.registrar_producto(
        Producto("TEC-1", "Teclado", "", 2500000, 2)
    )

    clientes = tabla_clientes([cliente])
    productos = tabla_productos([producto])

    assert "Ana" in clientes and "ana@ejemplo.cl" in clientes
    assert "TEC-1" in productos and "$25.000" in productos
    assert tabla_clientes([]) == "Sin clientes registrados."


def test_menu_principal_permite_salir_sin_error(base_pruebas) -> None:
    entradas = iter(["0"])
    salidas: list[str] = []

    menu_principal(
        TiendaServicio(),
        entrada=lambda _: next(entradas),
        salida=salidas.append,
    )

    assert salidas[-1] == "Programa finalizado."


def test_menu_principal_rechaza_opcion_inexistente_y_continua(base_pruebas) -> None:
    entradas = iter(["9", "0"])
    salidas: list[str] = []

    menu_principal(
        TiendaServicio(),
        entrada=lambda _: next(entradas),
        salida=salidas.append,
    )

    assert "Opción inválida." in salidas
    assert salidas[-1] == "Programa finalizado."
