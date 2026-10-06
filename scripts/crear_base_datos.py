from datos.conexion import BaseDeDatos


def main() -> None:
    base_datos = BaseDeDatos()
    base_datos.inicializar()
    if not base_datos.probar_conexion():
        raise RuntimeError("La base fue creada, pero la prueba de conexión falló.")
    print(f"Base '{base_datos.nombre}' lista en {base_datos.servidor}.")


if __name__ == "__main__":
    main()
