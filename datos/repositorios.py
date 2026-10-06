"""Consultas SQL de la tienda, aisladas de la interfaz y del dominio."""

import mysql.connector

from datos.conexion import BaseDeDatos
from datos.models import cliente_desde_fila, pedido_desde_fila, producto_desde_fila
from negocio.entidades import Cliente, DetallePedido, Pedido, Producto


class TiendaRepositorio:
    def __init__(self, base_datos: BaseDeDatos) -> None:
        self._base_datos = base_datos

    def guardar_cliente(self, cliente: Cliente) -> None:
        try:
            with self._base_datos.transaccion() as conexion:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO clientes (nombre, correo) VALUES (%s, %s)",
                        (cliente.nombre, cliente.correo),
                    )
                    cliente._asignar_id(cursor.lastrowid)
        except mysql.connector.IntegrityError as error:
            raise ValueError("No se pudo registrar; el correo puede estar repetido.") from error

    def guardar_producto(self, producto: Producto) -> None:
        with self._base_datos.transaccion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO productos
                       (nombre, descripcion, precio_centavos, stock)
                       VALUES (%s, %s, %s, %s)""",
                    (producto.nombre, producto.descripcion,
                     producto.precio_centavos, producto.stock),
                )
                producto._asignar_id(cursor.lastrowid)

    def guardar_pedido(self, pedido: Pedido) -> None:
        try:
            with self._base_datos.transaccion() as conexion:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO pedidos (cliente_id, estado) VALUES (%s, %s)",
                        (pedido.cliente.id, pedido.estado),
                    )
                    pedido._asignar_id(cursor.lastrowid)
        except mysql.connector.IntegrityError as error:
            raise ValueError("El cliente no existe en la base de datos.") from error

    def guardar_detalle(self, pedido: Pedido, detalle: DetallePedido) -> None:
        try:
            with self._base_datos.transaccion() as conexion:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        """UPDATE productos SET stock = stock - %s
                           WHERE id = %s AND stock >= %s""",
                        (detalle.cantidad, detalle.producto.id, detalle.cantidad),
                    )
                    if cursor.rowcount != 1:
                        raise ValueError("No existe stock suficiente para el producto.")
                    cursor.execute(
                        """UPDATE pedidos SET total_centavos = total_centavos + %s
                           WHERE id = %s AND estado = 'CREADO'""",
                        (detalle.subtotal_centavos, pedido.id),
                    )
                    if cursor.rowcount != 1:
                        raise ValueError("El pedido no existe o ya no puede modificarse.")
                    cursor.execute(
                        """INSERT INTO detalles_pedido
                           (pedido_id, producto_id, cantidad,
                            precio_unitario_centavos, subtotal_centavos)
                           VALUES (%s, %s, %s, %s, %s)""",
                        (pedido.id, detalle.producto.id, detalle.cantidad,
                         detalle.precio_unitario_centavos, detalle.subtotal_centavos),
                    )
                    detalle._asignar_id(cursor.lastrowid)
        except mysql.connector.IntegrityError as error:
            raise ValueError("No se pudo agregar el producto al pedido.") from error

    def obtener_cliente(self, identificador: int) -> Cliente:
        fila = self._una_fila(
            "SELECT id, nombre, correo FROM clientes WHERE id = %s", (identificador,)
        )
        if fila is None:
            raise ValueError("No existe un cliente con ese identificador.")
        return cliente_desde_fila(fila)

    def obtener_producto(self, identificador: int) -> Producto:
        fila = self._una_fila(
            """SELECT id, nombre, descripcion, precio_centavos, stock
               FROM productos WHERE id = %s""", (identificador,)
        )
        if fila is None:
            raise ValueError("No existe un producto con ese identificador.")
        return producto_desde_fila(fila)

    def obtener_pedido(self, identificador: int) -> Pedido:
        fila = self._una_fila(
            """SELECT p.id, p.estado, p.total_centavos,
                      c.id AS cliente_id, c.nombre, c.correo
               FROM pedidos p JOIN clientes c ON c.id = p.cliente_id
               WHERE p.id = %s""", (identificador,)
        )
        if fila is None:
            raise ValueError("No existe un pedido con ese identificador.")
        return pedido_desde_fila(fila)

    def resumen(self) -> tuple[list[dict], list[dict], list[dict]]:
        conexion = self._base_datos.conectar()
        try:
            with conexion.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT id, nombre, correo FROM clientes ORDER BY id")
                clientes = cursor.fetchall()
                cursor.execute(
                    "SELECT id, nombre, precio_centavos, stock FROM productos ORDER BY id"
                )
                productos = cursor.fetchall()
                cursor.execute(
                    """SELECT p.id, c.nombre AS cliente, p.estado,
                              p.total_centavos, p.creado_en
                       FROM pedidos p JOIN clientes c ON c.id = p.cliente_id
                       ORDER BY p.id"""
                )
                pedidos = cursor.fetchall()
            return clientes, productos, pedidos
        finally:
            conexion.close()

    def _una_fila(self, consulta: str, parametros: tuple[int]) -> dict | None:
        conexion = self._base_datos.conectar()
        try:
            with conexion.cursor(dictionary=True) as cursor:
                cursor.execute(consulta, parametros)
                return cursor.fetchone()
        finally:
            conexion.close()
