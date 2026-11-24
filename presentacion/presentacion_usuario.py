"""Formularios de consola y tablas para administrar usuarios."""

from collections.abc import Callable, Sequence
from datetime import date
from getpass import getpass

from prettytable import PrettyTable

from auxiliares.info_app import NOMBRE_APLICACION, VERSION_APLICACION
from auxiliares.validaciones import (
    validar_contrasenia,
    validar_correo,
    validar_dato_obligatorio,
    validar_dato_opcional,
    validar_fecha_nacimiento,
    validar_genero,
    validar_rut,
)
from datos.modelos import PaisModelo, UsuarioModelo
from negocio import ErrorDominio, TiendaServicio
from presentacion.entradas import Entrada, Salida


LectorContrasenia = Callable[[str], str]


def _solicitar_validado(
    mensaje: str,
    validador: Callable[[str], object],
    *,
    entrada: Entrada,
    salida: Salida,
    opcional: bool = False,
):
    while True:
        valor = entrada(mensaje).strip()
        if opcional and not valor:
            return None
        try:
            return validador(valor)
        except ValueError as error:
            salida(str(error))


def solicitar_rut(
    mensaje: str,
    *,
    entrada: Entrada = input,
    salida: Salida = print,
    opcional: bool = False,
) -> str | None:
    return _solicitar_validado(
        mensaje, validar_rut, entrada=entrada, salida=salida, opcional=opcional
    )


def solicitar_dato_obligatorio(
    mensaje: str, *, entrada: Entrada = input, salida: Salida = print
) -> str:
    return _solicitar_validado(
        mensaje, validar_dato_obligatorio, entrada=entrada, salida=salida
    )


def solicitar_dato_opcional(
    mensaje: str, *, entrada: Entrada = input, salida: Salida = print
) -> str | None:
    return _solicitar_validado(
        mensaje,
        validar_dato_opcional,
        entrada=entrada,
        salida=salida,
        opcional=True,
    )


def solicitar_correo(
    mensaje: str,
    *,
    entrada: Entrada = input,
    salida: Salida = print,
    opcional: bool = False,
) -> str | None:
    return _solicitar_validado(
        mensaje, validar_correo, entrada=entrada, salida=salida, opcional=opcional
    )


def tabla_paises(paises: Sequence[PaisModelo]) -> str:
    tabla = PrettyTable(["ID", "País", "Nacionalidad"])
    tabla.align = "l"
    for pais in paises:
        tabla.add_row([pais.id_pais, pais.pais, pais.nacionalidad or "-"])
    return tabla.get_string()


def solicitar_pais(
    servicio: TiendaServicio,
    *,
    entrada: Entrada = input,
    salida: Salida = print,
    opcional: bool = False,
) -> int | None:
    while True:
        nombre = entrada(
            "País (ENTER para conservar): " if opcional else "País: "
        ).strip()
        if opcional and not nombre:
            return None
        if not nombre:
            salida("El país es obligatorio.")
            continue
        paises = servicio.listar_paises(nombre)
        if not paises:
            salida("No se encontraron países habilitados con ese nombre.")
            continue
        salida(tabla_paises(paises))
        ids = {pais.id_pais for pais in paises}
        while True:
            valor = entrada("ID del país: ").strip()
            if not valor.isdecimal() or int(valor) not in ids:
                salida("El ID debe corresponder a uno de los países mostrados.")
                continue
            return int(valor)


def solicitar_fecha_nacimiento(
    mensaje: str,
    *,
    entrada: Entrada = input,
    salida: Salida = print,
    opcional: bool = False,
) -> date | None:
    return _solicitar_validado(
        mensaje,
        validar_fecha_nacimiento,
        entrada=entrada,
        salida=salida,
        opcional=opcional,
    )


def solicitar_genero(
    mensaje: str,
    *,
    entrada: Entrada = input,
    salida: Salida = print,
    opcional: bool = False,
) -> int | None:
    salida("Opciones de género: [1] Masculino [2] Femenino [3] Otro")
    return _solicitar_validado(
        mensaje, validar_genero, entrada=entrada, salida=salida, opcional=opcional
    )


def _leer_contrasenia_oculta(mensaje: str) -> str:
    try:
        import maskpass

        return maskpass.askpass(prompt=mensaje, mask="*")
    except (ImportError, OSError, RuntimeError):
        return getpass(mensaje)


def solicitar_contrasenia(
    mensaje: str,
    *,
    lector_contrasenia: LectorContrasenia | None = None,
    salida: Salida = print,
) -> str:
    lector = lector_contrasenia or _leer_contrasenia_oculta
    while True:
        try:
            return validar_contrasenia(lector(mensaje))
        except ValueError as error:
            salida(str(error))


def tabla_usuarios(usuarios: Sequence[UsuarioModelo]) -> str:
    if not usuarios:
        return "Sin usuarios registrados."
    tabla = PrettyTable(
        ["ID", "RUT", "Nombre completo", "Correo", "País", "Nacimiento", "Género", "Estado"]
    )
    tabla.align = "l"
    generos = {1: "Masculino", 2: "Femenino", 3: "Otro"}
    for usuario in usuarios:
        tabla.add_row(
            [
                usuario.id_usuario,
                usuario.rut,
                f"{usuario.nombre} {usuario.apellido}",
                usuario.correo,
                usuario.pais.pais,
                usuario.fecha_nacimiento.strftime("%d/%m/%Y"),
                generos[usuario.genero],
                "Habilitado" if usuario.habilitado else "Deshabilitado",
            ]
        )
    return tabla.get_string()


def mostrar_listado_usuarios(
    servicio: TiendaServicio,
    *,
    habilitado: bool | None = True,
    salida: Salida = print,
) -> str:
    resultado = tabla_usuarios(servicio.listar_usuarios(habilitado))
    salida(resultado)
    return resultado


def mostrar_usuario_por_rut(
    servicio: TiendaServicio,
    *,
    entrada: Entrada = input,
    salida: Salida = print,
) -> UsuarioModelo:
    rut = solicitar_rut("RUT del usuario: ", entrada=entrada, salida=salida)
    usuario = servicio.buscar_usuario_rut(rut)
    salida(tabla_usuarios([usuario]))
    return usuario


def mostrar_usuario_por_correo(
    servicio: TiendaServicio,
    *,
    entrada: Entrada = input,
    salida: Salida = print,
) -> UsuarioModelo:
    correo = solicitar_correo(
        "Correo del usuario: ", entrada=entrada, salida=salida
    )
    usuario = servicio.buscar_usuario_correo(correo)
    salida(tabla_usuarios([usuario]))
    return usuario


def crear_usuario(
    servicio: TiendaServicio,
    *,
    entrada: Entrada = input,
    salida: Salida = print,
    lector_contrasenia: LectorContrasenia | None = None,
) -> UsuarioModelo:
    return _crear_usuario_con(
        servicio.registrar_usuario,
        servicio,
        entrada=entrada,
        salida=salida,
        lector_contrasenia=lector_contrasenia,
    )


def _crear_usuario_con(
    registrar: Callable[..., UsuarioModelo],
    servicio: TiendaServicio,
    *,
    entrada: Entrada,
    salida: Salida,
    lector_contrasenia: LectorContrasenia | None,
) -> UsuarioModelo:
    salida("\nIngrese los datos del usuario")
    usuario = registrar(
        rut=solicitar_rut("RUT (11.111.111-1): ", entrada=entrada, salida=salida),
        nombre=solicitar_dato_obligatorio("Nombre: ", entrada=entrada, salida=salida),
        apellido=solicitar_dato_obligatorio("Apellido: ", entrada=entrada, salida=salida),
        correo=solicitar_correo("Correo: ", entrada=entrada, salida=salida),
        pais_id=solicitar_pais(servicio, entrada=entrada, salida=salida),
        fecha_nacimiento=solicitar_fecha_nacimiento(
            "Fecha de nacimiento [dd/mm/aaaa]: ", entrada=entrada, salida=salida
        ),
        genero=solicitar_genero(
            "Seleccione género [1-3]: ", entrada=entrada, salida=salida
        ),
        contrasenia=solicitar_contrasenia(
            "Contraseña: ",
            lector_contrasenia=lector_contrasenia,
            salida=salida,
        ),
    )
    salida(f"Usuario registrado con ID {usuario.id_usuario}.")
    return usuario


def preparar_primer_usuario(
    servicio: TiendaServicio,
    *,
    entrada: Entrada = input,
    salida: Salida = print,
    lector_contrasenia: LectorContrasenia | None = None,
) -> UsuarioModelo:
    """Crea la primera cuenta solo durante una instalación vacía."""
    if servicio.estado_acceso_usuarios() != "sin_usuarios":
        raise ErrorDominio(
            "La preparación del primer usuario solo está disponible "
            "durante la instalación inicial."
        )
    if not servicio.listar_paises():
        raise ErrorDominio(
            "No existe un país habilitado para completar el primer usuario."
        )
    salida("Preparación inicial: cree la primera cuenta de acceso.")
    return _crear_usuario_con(
        servicio.registrar_primer_usuario,
        servicio,
        entrada=entrada,
        salida=salida,
        lector_contrasenia=lector_contrasenia,
    )


def modificar_usuario(
    servicio: TiendaServicio,
    *,
    entrada: Entrada = input,
    salida: Salida = print,
) -> UsuarioModelo:
    rut_actual = solicitar_rut(
        "RUT del usuario a modificar: ", entrada=entrada, salida=salida
    )
    actual = servicio.buscar_usuario_rut(rut_actual)
    salida(tabla_usuarios([actual]))
    actualizado = servicio.actualizar_usuario(
        actual.rut,
        rut=solicitar_rut(
            "Nuevo RUT (ENTER para conservar): ",
            entrada=entrada,
            salida=salida,
            opcional=True,
        ),
        nombre=solicitar_dato_opcional(
            "Nombre (ENTER para conservar): ", entrada=entrada, salida=salida
        ),
        apellido=solicitar_dato_opcional(
            "Apellido (ENTER para conservar): ", entrada=entrada, salida=salida
        ),
        correo=solicitar_correo(
            "Correo (ENTER para conservar): ",
            entrada=entrada,
            salida=salida,
            opcional=True,
        ),
        pais_id=solicitar_pais(
            servicio, entrada=entrada, salida=salida, opcional=True
        ),
        fecha_nacimiento=solicitar_fecha_nacimiento(
            "Fecha de nacimiento [dd/mm/aaaa] (ENTER para conservar): ",
            entrada=entrada,
            salida=salida,
            opcional=True,
        ),
        genero=solicitar_genero(
            "Género [1-3] (ENTER para conservar): ",
            entrada=entrada,
            salida=salida,
            opcional=True,
        ),
    )
    salida("Usuario actualizado.")
    return actualizado


def eliminar_usuario(
    servicio: TiendaServicio,
    *,
    entrada: Entrada = input,
    salida: Salida = print,
) -> UsuarioModelo | None:
    rut = solicitar_rut(
        "RUT del usuario a eliminar: ", entrada=entrada, salida=salida
    )
    usuario = servicio.buscar_usuario_rut(rut)
    salida(tabla_usuarios([usuario]))
    while True:
        confirmacion = entrada("¿Confirma la deshabilitación? [S/N]: ").strip().lower()
        if confirmacion == "n":
            salida("Operación cancelada.")
            return None
        if confirmacion == "s":
            deshabilitado = servicio.deshabilitar_usuario(usuario.rut)
            salida("Usuario deshabilitado.")
            return deshabilitado
        salida("Ingrese S para confirmar o N para cancelar.")


def login_usuario(
    servicio: TiendaServicio,
    *,
    entrada: Entrada = input,
    salida: Salida = print,
    lector_contrasenia: LectorContrasenia | None = None,
) -> UsuarioModelo | None:
    """Solicita credenciales sin aplicar las reglas de creación de claves."""
    salida(f"\n{NOMBRE_APLICACION} v{VERSION_APLICACION}")
    correo = solicitar_correo(
        "Correo (ENTER para cancelar): ",
        entrada=entrada,
        salida=salida,
        opcional=True,
    )
    if correo is None:
        salida("Inicio de sesión cancelado.")
        return None

    lector = lector_contrasenia or _leer_contrasenia_oculta
    contrasenia = lector("Contraseña (ENTER para cancelar): ")
    if not contrasenia:
        salida("Inicio de sesión cancelado.")
        return None

    usuario = servicio.autenticar_usuario(correo, contrasenia)
    salida(f"Bienvenida, {usuario.nombre}.")
    return usuario
