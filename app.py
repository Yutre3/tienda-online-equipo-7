"""Punto de entrada de la aplicación de tienda en línea."""

from collections.abc import Callable

from peewee import Database, PeeweeException

from datos.conexion import (
    base_datos_proxy,
    cargar_datos_demostracion,
    configurar_base_datos,
    crear_tablas,
)
from negocio import ErrorDominio, TiendaServicio
from presentacion.entradas import Entrada, Salida
from presentacion.menu import menu_principal
from presentacion.presentacion_usuario import (
    login_usuario,
    preparar_primer_usuario,
)


def crear_servicio(base: Database | None = None) -> TiendaServicio:
    usar_datos_demostracion = base is None
    base_configurada = configurar_base_datos(base)
    base_configurada.connect(reuse_if_open=True)
    crear_tablas()
    if usar_datos_demostracion:
        cargar_datos_demostracion()
    return TiendaServicio()


def _desea_reintentar(entrada: Entrada, salida: Salida) -> bool:
    while True:
        respuesta = entrada("¿Desea intentar nuevamente? [S/N]: ").strip().lower()
        if respuesta == "s":
            return True
        if respuesta == "n":
            return False
        salida("Ingrese S para reintentar o N para salir.")


def ejecutar_aplicacion(
    servicio: TiendaServicio,
    *,
    entrada: Entrada = input,
    salida: Salida = print,
    lector_contrasenia: Callable[[str], str] | None = None,
) -> int:
    """Exige autenticación antes de cada sesión de menú."""
    while True:
        estado = servicio.estado_acceso_usuarios()
        if estado == "sin_usuarios":
            try:
                preparar_primer_usuario(
                    servicio,
                    entrada=entrada,
                    salida=salida,
                    lector_contrasenia=lector_contrasenia,
                )
            except ErrorDominio as error:
                salida(f"No fue posible preparar el primer usuario: {error}")
                return 2
            continue
        if estado == "sin_password_valido":
            salida(
                "Existen usuarios, pero ninguna cuenta habilitada tiene una "
                "contraseña válida. Ejecute localmente: "
                "python -m auxiliares.recuperar_acceso"
            )
            return 2
        if estado == "sin_habilitados":
            salida(
                "No existen cuentas habilitadas. La recuperación de contraseña "
                "no habilita ni crea cuentas."
            )
            return 2

        try:
            usuario = login_usuario(
                servicio,
                entrada=entrada,
                salida=salida,
                lector_contrasenia=lector_contrasenia,
            )
        except ErrorDominio as error:
            salida(str(error))
            if _desea_reintentar(entrada, salida):
                continue
            salida("Programa finalizado.")
            return 0

        if usuario is None:
            if _desea_reintentar(entrada, salida):
                continue
            salida("Programa finalizado.")
            return 0

        menu_principal(servicio, entrada=entrada, salida=salida)


def main() -> int:
    try:
        servicio = crear_servicio()
        print("Conexión exitosa. Base de datos preparada.")
        return ejecutar_aplicacion(servicio)
    except (EOFError, KeyboardInterrupt):
        print("\nEjecución cancelada de forma segura.")
        return 0
    except ValueError as error:
        print(
            "La configuración de la base de datos no es válida. "
            "Revise DB_PORT y los demás valores de .env.\n"
            f"Detalle técnico: {error}"
        )
        return 1
    except PeeweeException as error:
        print(
            "No fue posible conectar con la base de datos. "
            "Revise MySQL/XAMPP y el archivo .env.\n"
            f"Detalle técnico: {error}"
        )
        return 1
    finally:
        try:
            if not base_datos_proxy.is_closed():
                base_datos_proxy.close()
        except (AttributeError, PeeweeException):
            pass


if __name__ == "__main__":
    raise SystemExit(main())
