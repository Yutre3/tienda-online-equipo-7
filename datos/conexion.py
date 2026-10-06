"""Conexión y creación reproducible de la base de datos."""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import mysql.connector
from mysql.connector.connection import MySQLConnection

from datos.configuracion import ConfiguracionBD


RUTA_ESQUEMA = Path(__file__).resolve().parent / "sql" / "001_esquema.sql"


class BaseDeDatos:
    """Administra conexiones y transacciones con MariaDB/MySQL."""

    def __init__(self, configuracion: ConfiguracionBD | None = None) -> None:
        self._configuracion = configuracion or ConfiguracionBD.desde_entorno()

    @property
    def nombre(self) -> str:
        return self._configuracion.nombre

    @property
    def servidor(self) -> str:
        return f"{self._configuracion.host}:{self._configuracion.puerto}"

    def conectar(self, incluir_base: bool = True) -> MySQLConnection:
        parametros: dict[str, object] = {
            "host": self._configuracion.host,
            "port": self._configuracion.puerto,
            "user": self._configuracion.usuario,
            "password": self._configuracion.contrasena,
            "charset": "utf8mb4",
            "autocommit": False,
        }
        if incluir_base:
            parametros["database"] = self.nombre
        return mysql.connector.connect(**parametros)

    @contextmanager
    def transaccion(self) -> Iterator[MySQLConnection]:
        conexion = self.conectar()
        try:
            yield conexion
            conexion.commit()
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

    def inicializar(self) -> None:
        if not RUTA_ESQUEMA.is_file():
            raise FileNotFoundError(f"No se encontró el esquema: {RUTA_ESQUEMA}")

        conexion = self.conectar(incluir_base=False)
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{self.nombre}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            conexion.commit()
        finally:
            conexion.close()

        sentencias: list[str] = []
        acumulada: list[str] = []
        for linea in RUTA_ESQUEMA.read_text(encoding="utf-8").splitlines():
            limpia = linea.strip()
            if not limpia or limpia.startswith("--"):
                continue
            acumulada.append(linea)
            if limpia.endswith(";"):
                sentencias.append("\n".join(acumulada).rstrip(";\n "))
                acumulada = []

        with self.transaccion() as conexion:
            with conexion.cursor() as cursor:
                for sentencia in sentencias:
                    if sentencia.upper().startswith(("CREATE DATABASE", "USE ")):
                        continue
                    cursor.execute(sentencia)

    def probar_conexion(self) -> bool:
        try:
            conexion = self.conectar()
            try:
                with conexion.cursor() as cursor:
                    cursor.execute("SELECT 1, DATABASE()")
                    return cursor.fetchone() == (1, self.nombre)
            finally:
                conexion.close()
        except mysql.connector.Error:
            return False

    def listar_tablas(self) -> set[str]:
        conexion = self.conectar()
        try:
            with conexion.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                return {fila[0] for fila in cursor.fetchall()}
        finally:
            conexion.close()
