from base_datos import BaseDeDatos


def main() -> None:
    base_datos = BaseDeDatos()
    if not base_datos.probar_conexion():
        print("No fue posible conectar con MariaDB de XAMPP.")
        raise SystemExit(1)
    print(
        f"Conexión exitosa con '{base_datos.nombre}' "
        f"en {base_datos.servidor}."
    )


if __name__ == "__main__":
    main()
