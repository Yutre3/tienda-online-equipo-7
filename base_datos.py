from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path
from collections.abc import Iterator

import mysql.connector
from mysql.connector.connection import MySQLConnection


DIRECTORIO_PROYECTO = Path(__file__).resolve().parent
RUTA_ESQUEMA = DIRECTORIO_PROYECTO / "schema.sql"


class BaseDeDatos:
    """Administra la conexión con MariaDB incluida en XAMPP."""

    def __init__(self) -> None:
        self._host = os.getenv("DB_HOST", "127.0.0.1")
        self._puerto = int(os.getenv("DB_PORT", "3306"))
        self._base = os.getenv("DB_NAME", "tienda_online")
        self._usuario = os.getenv("DB_USER", "root")
        self._contrasena = os.getenv("DB_PASSWORD", "")

    @property
    def nombre(self) -> str:
        return self._base

    @property
    def servidor(self) -> str:
        return f"{self._host}:{self._puerto}"

    def conectar(self, incluir_base: bool = True) -> MySQLConnection:
        parametros: dict[str, object] = {
            "host": self._host,
            "port": self._puerto,
            "user": self._usuario,
            "password": self._contrasena,
            "charset": "utf8mb4",
            "autocommit": False,
        }
        if incluir_base:
            parametros["database"] = self._base
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
        if not RUTA_ESQUEMA.exists():
            raise FileNotFoundError(f"No se encontró el esquema: {RUTA_ESQUEMA}")

        conexion = self.conectar(incluir_base=False)
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{self._base}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            conexion.commit()
        finally:
            conexion.close()

        sentencias = []
        acumulada = []
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
                    resultado = cursor.fetchone()
                return resultado == (1, self._base)
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
