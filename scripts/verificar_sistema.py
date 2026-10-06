from datos.conexion import BaseDeDatos


TABLAS = {"clientes", "productos", "pedidos", "detalles_pedido"}


def main() -> None:
    base_datos = BaseDeDatos()
    base_datos.inicializar()
    if not base_datos.probar_conexion():
        raise RuntimeError("Falló la conexión con MariaDB.")
    faltantes = TABLAS - base_datos.listar_tablas()
    if faltantes:
        raise RuntimeError(f"Faltan tablas: {', '.join(sorted(faltantes))}")

    conexion = base_datos.conectar()
    try:
        with conexion.cursor() as cursor:
            marcadores = ", ".join(["%s"] * len(TABLAS))
            cursor.execute(
                f"""SELECT COUNT(*) FROM information_schema.TABLES
                    WHERE TABLE_SCHEMA = %s AND ENGINE = 'InnoDB'
                      AND TABLE_NAME IN ({marcadores})""",
                (base_datos.nombre, *sorted(TABLAS)),
            )
            tablas_innodb = cursor.fetchone()[0]
            cursor.execute(
                """SELECT COUNT(*)
                   FROM information_schema.REFERENTIAL_CONSTRAINTS
                   WHERE CONSTRAINT_SCHEMA = %s""",
                (base_datos.nombre,),
            )
            relaciones = cursor.fetchone()[0]
    finally:
        conexion.close()

    if tablas_innodb != len(TABLAS):
        raise RuntimeError("No todas las tablas utilizan el motor InnoDB.")
    if relaciones != 3:
        raise RuntimeError(
            f"Se esperaban 3 claves foráneas y se encontraron {relaciones}."
        )
    print(f"[OK] Conexión con {base_datos.nombre} en {base_datos.servidor}")
    print(f"[OK] Tablas InnoDB: {', '.join(sorted(TABLAS))}")
    print("[OK] Tres claves foráneas activas")
    print("Sistema verificado y operativo.")


if __name__ == "__main__":
    main()
