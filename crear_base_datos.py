from base_datos import BaseDeDatos


def main() -> None:
    base_datos = BaseDeDatos()
    base_datos.inicializar()
    if not base_datos.probar_conexion():
        raise RuntimeError("La base de datos fue creada, pero la conexión falló.")
    print(
        f"Base de datos '{base_datos.nombre}' creada en "
        f"{base_datos.servidor} y conexión exitosa."
    )


if __name__ == "__main__":
    main()
