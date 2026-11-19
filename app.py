"""Punto de entrada de la aplicación de tienda en línea."""

from peewee import Database, PeeweeException

from datos.conexion import (
    base_datos_proxy,
    cargar_datos_demostracion,
    configurar_base_datos,
    crear_tablas,
)
from negocio import TiendaServicio
from presentacion.menu import menu_principal


def crear_servicio(base: Database | None = None) -> TiendaServicio:
    usar_datos_demostracion = base is None
    base_configurada = configurar_base_datos(base)
    base_configurada.connect(reuse_if_open=True)
    crear_tablas()
    if usar_datos_demostracion:
        cargar_datos_demostracion()
    return TiendaServicio()


def main() -> int:
    try:
        servicio = crear_servicio()
        print("Conexión exitosa. Base de datos preparada.")
        menu_principal(servicio)
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
