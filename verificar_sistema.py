from __future__ import annotations

import subprocess
import sys

import mysql.connector

from base_datos import BaseDeDatos


TABLAS_REQUERIDAS = {
    "clientes",
    "productos",
    "pedidos",
    "detalles_pedido",
}


def verificar_xampp() -> None:
    comando = ["/opt/lampp/lampp", "status"]
    resultado = subprocess.run(comando, capture_output=True, text=True, check=False)
    salida = f"{resultado.stdout}\n{resultado.stderr}".lower()
    if resultado.returncode != 0 or "mysql is running" not in salida:
        raise RuntimeError(
            "MariaDB de XAMPP no está iniciado. Ejecute: "
            "sudo /opt/lampp/lampp start"
        )
    print("[OK] MariaDB de XAMPP está iniciado")


def verificar_base_datos() -> None:
    base_datos = BaseDeDatos()
    base_datos.inicializar()
    if not base_datos.probar_conexion():
        raise RuntimeError("Falló la conexión con MariaDB de XAMPP.")

    tablas = base_datos.listar_tablas()
    faltantes = TABLAS_REQUERIDAS - tablas
    if faltantes:
        raise RuntimeError(f"Faltan tablas: {', '.join(sorted(faltantes))}")

    conexion = base_datos.conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = %s AND ENGINE = 'InnoDB'
                  AND TABLE_NAME IN ('clientes', 'productos', 'pedidos',
                                     'detalles_pedido')
                """,
                (base_datos.nombre,),
            )
            tablas_innodb = cursor.fetchone()[0]
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.REFERENTIAL_CONSTRAINTS
                WHERE CONSTRAINT_SCHEMA = %s
                """,
                (base_datos.nombre,),
            )
            relaciones = cursor.fetchone()[0]
    finally:
        conexion.close()

    if tablas_innodb != len(TABLAS_REQUERIDAS):
        raise RuntimeError("No todas las tablas utilizan InnoDB.")
    if relaciones != 3:
        raise RuntimeError("No se encontraron las tres claves foráneas esperadas.")

    print(f"[OK] Conexión con {base_datos.nombre} en {base_datos.servidor}")
    print(f"[OK] Tablas InnoDB: {', '.join(sorted(TABLAS_REQUERIDAS))}")
    print("[OK] Tres claves foráneas activas")


def main() -> None:
    try:
        verificar_xampp()
        verificar_base_datos()
    except (OSError, mysql.connector.Error, RuntimeError) as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        raise SystemExit(1) from error
    print("Sistema XAMPP verificado y operativo.")


if __name__ == "__main__":
    main()
