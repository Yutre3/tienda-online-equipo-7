"""Procedimiento local explícito para cambiar la clave de una cuenta existente."""

from collections.abc import Callable

from peewee import PeeweeException

from datos.conexion import base_datos_proxy
from negocio import ErrorDominio, TiendaServicio
from presentacion.entradas import Entrada, Salida
from presentacion.presentacion_usuario import (
    solicitar_contrasenia,
    solicitar_correo,
)


def main(
    *,
    servicio: TiendaServicio | None = None,
    entrada: Entrada = input,
    salida: Salida = print,
    lector_contrasenia: Callable[[str], str] | None = None,
) -> int:
    propia_conexion = servicio is None
    try:
        if servicio is None:
            from app import crear_servicio

            servicio = crear_servicio()
        salida("Recuperación local de una cuenta existente.")
        correo = solicitar_correo("Correo: ", entrada=entrada, salida=salida)
        contrasenia = solicitar_contrasenia(
            "Nueva contraseña: ",
            lector_contrasenia=lector_contrasenia,
            salida=salida,
        )
        servicio.cambiar_contrasenia_usuario_existente(correo, contrasenia)
        salida("Contraseña actualizada. El estado de la cuenta no fue modificado.")
        return 0
    except (EOFError, KeyboardInterrupt):
        salida("Recuperación cancelada de forma segura.")
        return 0
    except (ErrorDominio, PeeweeException, ValueError) as error:
        salida(f"No fue posible recuperar el acceso: {error}")
        return 1
    finally:
        if propia_conexion:
            try:
                if not base_datos_proxy.is_closed():
                    base_datos_proxy.close()
            except (AttributeError, PeeweeException):
                pass


if __name__ == "__main__":
    raise SystemExit(main())
