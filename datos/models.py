"""Modelos POO, conexión y persistencia de la tienda en línea."""

from __future__ import annotations

from abc import ABC
from collections.abc import Iterator
from contextlib import contextmanager
import os
from pathlib import Path
import re

import mysql.connector
from mysql.connector.connection import MySQLConnection


RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
RUTA_ESQUEMA = Path(__file__).resolve().parent / "sql" / "2026.10.05_20.00_DDL_Tienda_Online.sql"


def _cargar_env() -> None:
    ruta = RAIZ_PROYECTO / ".env"
    if not ruta.exists():
        return
    for numero, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        if "=" not in linea:
            raise ValueError(f"Línea {numero} inválida en .env.")
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip().strip("\"'"))


class BaseDeDatos:
    """Administra la conexión y las transacciones con MariaDB/MySQL."""

    def __init__(self) -> None:
        _cargar_env()
        self._host = os.getenv("DB_HOST", "127.0.0.1")
        self._puerto = int(os.getenv("DB_PORT", "3306"))
        self._nombre = os.getenv("DB_NAME", "tienda_online")
        self._usuario = os.getenv("DB_USER", "root")
        self._contrasena = os.getenv("DB_PASSWORD", "")
        if not re.fullmatch(r"[A-Za-z0-9_]+", self._nombre):
            raise ValueError("DB_NAME solo puede contener letras, números y guion bajo.")

    @property
    def nombre(self) -> str:
        return self._nombre

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
            parametros["database"] = self._nombre
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
                    f"CREATE DATABASE IF NOT EXISTS `{self._nombre}` "
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
                    if not sentencia.upper().startswith(("CREATE DATABASE", "USE ")):
                        cursor.execute(sentencia)

    def probar_conexion(self) -> bool:
        try:
            conexion = self.conectar()
            try:
                with conexion.cursor() as cursor:
                    cursor.execute("SELECT 1, DATABASE()")
                    return cursor.fetchone() == (1, self._nombre)
            finally:
                conexion.close()
        except mysql.connector.Error:
            return False


class Entidad(ABC):
    def __init__(self, identificador: int | None = None) -> None:
        if identificador is not None and identificador <= 0:
            raise ValueError("El identificador debe ser positivo.")
        self._id = identificador

    @property
    def id(self) -> int | None:
        return self._id

    def _asignar_id(self, identificador: int) -> None:
        if identificador <= 0 or self._id is not None:
            raise ValueError("No se puede asignar el identificador.")
        self._id = identificador


class Cliente(Entidad):
    def __init__(self, nombre: str, correo: str, identificador: int | None = None) -> None:
        super().__init__(identificador)
        self.nombre = nombre
        self.correo = correo

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        valor = valor.strip()
        if not valor:
            raise ValueError("El nombre del cliente es obligatorio.")
        self._nombre = valor

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        valor = valor.strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", valor):
            raise ValueError("El correo del cliente no es válido.")
        self._correo = valor


class Producto(Entidad):
    def __init__(self, nombre: str, descripcion: str, precio_centavos: int,
                 stock: int, identificador: int | None = None) -> None:
        super().__init__(identificador)
        self.nombre = nombre
        self.descripcion = descripcion.strip()
        self.precio_centavos = precio_centavos
        self.stock = stock

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        valor = valor.strip()
        if not valor:
            raise ValueError("El nombre del producto es obligatorio.")
        self._nombre = valor

    @property
    def precio_centavos(self) -> int:
        return self._precio_centavos

    @precio_centavos.setter
    def precio_centavos(self, valor: int) -> None:
        if not isinstance(valor, int) or isinstance(valor, bool) or valor <= 0:
            raise ValueError("El precio debe ser un entero positivo.")
        self._precio_centavos = valor

    @property
    def stock(self) -> int:
        return self._stock

    @stock.setter
    def stock(self, valor: int) -> None:
        if not isinstance(valor, int) or isinstance(valor, bool) or valor < 0:
            raise ValueError("El stock no puede ser negativo.")
        self._stock = valor

    def descontar_stock(self, cantidad: int) -> None:
        if cantidad <= 0 or cantidad > self._stock:
            raise ValueError("No existe stock suficiente para el producto.")
        self._stock -= cantidad


class DetallePedido(Entidad):
    def __init__(self, producto: Producto, cantidad: int,
                 identificador: int | None = None) -> None:
        super().__init__(identificador)
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser positiva.")
        self.producto = producto
        self.cantidad = cantidad
        self.precio_unitario_centavos = producto.precio_centavos

    @property
    def subtotal_centavos(self) -> int:
        return self.cantidad * self.precio_unitario_centavos


class Pedido(Entidad):
    def __init__(self, cliente: Cliente, estado: str = "CREADO",
                 total_centavos: int = 0, identificador: int | None = None) -> None:
        super().__init__(identificador)
        self.cliente = cliente
        self.estado = estado
        self.total_centavos = total_centavos
        self.detalles: list[DetallePedido] = []

    def agregar_detalle(self, detalle: DetallePedido) -> None:
        if self.estado != "CREADO":
            raise ValueError("Solo se pueden modificar pedidos creados.")
        self.detalles.append(detalle)
        self.total_centavos += detalle.subtotal_centavos


class TiendaRepositorio:
    """Centraliza las consultas SQL de la tienda."""

    def __init__(self, base_datos: BaseDeDatos) -> None:
        self._base = base_datos

    def guardar_cliente(self, cliente: Cliente) -> None:
        with self._base.transaccion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute("INSERT INTO clientes (nombre, correo) VALUES (%s, %s)",
                               (cliente.nombre, cliente.correo))
                cliente._asignar_id(cursor.lastrowid)

    def guardar_producto(self, producto: Producto) -> None:
        with self._base.transaccion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO productos (nombre, descripcion, precio_centavos, stock) "
                    "VALUES (%s, %s, %s, %s)",
                    (producto.nombre, producto.descripcion,
                     producto.precio_centavos, producto.stock),
                )
                producto._asignar_id(cursor.lastrowid)

    def guardar_pedido(self, pedido: Pedido) -> None:
        with self._base.transaccion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute("INSERT INTO pedidos (cliente_id, estado) VALUES (%s, %s)",
                               (pedido.cliente.id, pedido.estado))
                pedido._asignar_id(cursor.lastrowid)

    def guardar_detalle(self, pedido: Pedido, detalle: DetallePedido) -> None:
        with self._base.transaccion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "UPDATE productos SET stock = stock - %s "
                    "WHERE id = %s AND stock >= %s",
                    (detalle.cantidad, detalle.producto.id, detalle.cantidad),
                )
                if cursor.rowcount != 1:
                    raise ValueError("No existe stock suficiente.")
                cursor.execute(
                    "UPDATE pedidos SET total_centavos = total_centavos + %s "
                    "WHERE id = %s AND estado = 'CREADO'",
                    (detalle.subtotal_centavos, pedido.id),
                )
                if cursor.rowcount != 1:
                    raise ValueError("El pedido no puede modificarse.")
                cursor.execute(
                    "INSERT INTO detalles_pedido "
                    "(pedido_id, producto_id, cantidad, precio_unitario_centavos, subtotal_centavos) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (pedido.id, detalle.producto.id, detalle.cantidad,
                     detalle.precio_unitario_centavos, detalle.subtotal_centavos),
                )
                detalle._asignar_id(cursor.lastrowid)

    def obtener_cliente(self, identificador: int) -> Cliente:
        fila = self._fila("SELECT id, nombre, correo FROM clientes WHERE id = %s",
                          (identificador,))
        if fila is None:
            raise ValueError("No existe el cliente.")
        return Cliente(fila["nombre"], fila["correo"], fila["id"])

    def obtener_producto(self, identificador: int) -> Producto:
        fila = self._fila(
            "SELECT id, nombre, descripcion, precio_centavos, stock "
            "FROM productos WHERE id = %s", (identificador,)
        )
        if fila is None:
            raise ValueError("No existe el producto.")
        return Producto(fila["nombre"], fila["descripcion"], fila["precio_centavos"],
                        fila["stock"], fila["id"])

    def obtener_pedido(self, identificador: int) -> Pedido:
        fila = self._fila(
            "SELECT p.id, p.estado, p.total_centavos, c.id AS cliente_id, "
            "c.nombre, c.correo FROM pedidos p JOIN clientes c "
            "ON c.id = p.cliente_id WHERE p.id = %s", (identificador,)
        )
        if fila is None:
            raise ValueError("No existe el pedido.")
        cliente = Cliente(fila["nombre"], fila["correo"], fila["cliente_id"])
        return Pedido(cliente, fila["estado"], fila["total_centavos"], fila["id"])

    def resumen(self) -> tuple[list[dict], list[dict], list[dict]]:
        conexion = self._base.conectar()
        try:
            with conexion.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT id, nombre, correo FROM clientes ORDER BY id")
                clientes = cursor.fetchall()
                cursor.execute("SELECT id, nombre, precio_centavos, stock "
                               "FROM productos ORDER BY id")
                productos = cursor.fetchall()
                cursor.execute("SELECT p.id, c.nombre AS cliente, p.estado, "
                               "p.total_centavos, p.creado_en FROM pedidos p "
                               "JOIN clientes c ON c.id = p.cliente_id ORDER BY p.id")
                pedidos = cursor.fetchall()
            return clientes, productos, pedidos
        finally:
            conexion.close()

    def _fila(self, consulta: str, parametros: tuple[int]) -> dict | None:
        conexion = self._base.conectar()
        try:
            with conexion.cursor(dictionary=True) as cursor:
                cursor.execute(consulta, parametros)
                return cursor.fetchone()
        finally:
            conexion.close()
