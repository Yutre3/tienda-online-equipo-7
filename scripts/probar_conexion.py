from datos.conexion import BaseDeDatos


def main() -> None:
    base_datos = BaseDeDatos()
    if not base_datos.probar_conexion():
        print("No fue posible conectar con MariaDB. Revise XAMPP y .env.")
        raise SystemExit(1)
    print(f"Conexión exitosa con '{base_datos.nombre}' en {base_datos.servidor}.")


if __name__ == "__main__":
    main()
