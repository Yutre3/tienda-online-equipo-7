from __future__ import annotations

import mysql.connector

from base_datos import BaseDeDatos
from modelos import Cliente, DetallePedido, Pedido, Producto


class TiendaServicio:
    """Coordina las operaciones del dominio y su persistencia en MariaDB."""

    def __init__(self, base_datos: BaseDeDatos) -> None:
        self._base_datos = base_datos

    def registrar_cliente(self, cliente: Cliente) -> Cliente:
        if cliente.id is not None:
            raise ValueError("El cliente ya está registrado.")
        try:
            with self._base_datos.transaccion() as conexion:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO clientes (nombre, correo) VALUES (%s, %s)",
                        (cliente.nombre, cliente.correo),
                    )
                    cliente._asignar_id(cursor.lastrowid)
        except mysql.connector.IntegrityError as error:
            raise ValueError("No se pudo registrar el cliente; revise el correo.") from error
        return cliente

    def registrar_producto(self, producto: Producto) -> Producto:
        if producto.id is not None:
            raise ValueError("El producto ya está registrado.")
        with self._base_datos.transaccion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO productos
                        (nombre, descripcion, precio_centavos, stock)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        producto.nombre,
                        producto.descripcion,
                        producto.precio_centavos,
                        producto.stock,
                    ),
                )
                producto._asignar_id(cursor.lastrowid)
        return producto

    def crear_pedido(self, cliente: Cliente) -> Pedido:
        if cliente.id is None:
            raise ValueError("El cliente debe estar registrado antes de crear un pedido.")
        pedido = Pedido(cliente)
        try:
            with self._base_datos.transaccion() as conexion:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO pedidos (cliente_id, estado) VALUES (%s, %s)",
                        (cliente.id, pedido.estado),
                    )
                    pedido._asignar_id(cursor.lastrowid)
        except mysql.connector.IntegrityError as error:
            raise ValueError("El cliente no existe en la base de datos.") from error
        return pedido

    def agregar_producto(
        self, pedido: Pedido, producto: Producto, cantidad: int
    ) -> DetallePedido:
        if pedido.id is None or producto.id is None:
            raise ValueError("El pedido y el producto deben estar registrados.")
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
            raise ValueError("La cantidad debe ser un entero positivo.")

        detalle = DetallePedido(producto, cantidad)
        try:
            with self._base_datos.transaccion() as conexion:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE productos SET stock = stock - %s
                        WHERE id = %s AND stock >= %s
                        """,
                        (cantidad, producto.id, cantidad),
                    )
                    if cursor.rowcount != 1:
                        raise ValueError("No existe stock suficiente para el producto.")

                    cursor.execute(
                        """
                        UPDATE pedidos SET total_centavos = total_centavos + %s
                        WHERE id = %s AND estado = 'CREADO'
                        """,
                        (detalle.subtotal_centavos, pedido.id),
                    )
                    if cursor.rowcount != 1:
                        raise ValueError("El pedido no existe o ya no puede modificarse.")

                    cursor.execute(
                        """
                        INSERT INTO detalles_pedido
                            (pedido_id, producto_id, cantidad,
                             precio_unitario_centavos, subtotal_centavos)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            pedido.id,
                            producto.id,
                            cantidad,
                            detalle.precio_unitario_centavos,
                            detalle.subtotal_centavos,
                        ),
                    )
                    detalle._asignar_id(cursor.lastrowid)
        except mysql.connector.IntegrityError as error:
            raise ValueError("No se pudo agregar el producto al pedido.") from error

        producto.descontar_stock(cantidad)
        pedido.agregar_detalle(detalle)
        return detalle

    def listar_productos(self) -> list[Producto]:
        conexion = self._base_datos.conectar()
        try:
            with conexion.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT id, nombre, descripcion, precio_centavos, stock
                    FROM productos ORDER BY id
                    """
                )
                filas = cursor.fetchall()
        finally:
            conexion.close()
        return [
            Producto(
                fila["nombre"],
                fila["descripcion"],
                fila["precio_centavos"],
                fila["stock"],
                fila["id"],
            )
            for fila in filas
        ]
