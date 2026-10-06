"""Punto de entrada de la aplicación de tienda en línea."""

import mysql.connector

from datos.models import BaseDeDatos, TiendaRepositorio
from negocio import TiendaServicio
from presentacion.menu import menu_principal


def main() -> None:
    try:
        base_datos = BaseDeDatos()
        base_datos.inicializar()
        if not base_datos.probar_conexion():
            raise mysql.connector.Error(
                "La prueba de conexión no respondió correctamente."
            )
        print(
            f"Conexión exitosa con la base '{base_datos.nombre}' "
            f"en {base_datos.servidor}."
        )
        repositorio = TiendaRepositorio(base_datos)
        menu_principal(TiendaServicio(repositorio), repositorio)
    except (mysql.connector.Error, FileNotFoundError, ValueError) as error:
        print(
            "No fue posible iniciar la aplicación. Revise XAMPP, la base y .env.\n"
            f"Detalle técnico: {error}"
        )
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
