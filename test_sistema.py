from __future__ import annotations

from uuid import uuid4
import unittest

import mysql.connector

from base_datos import BaseDeDatos
from modelos import Cliente, Producto
from servicios import TiendaServicio


class SistemaTiendaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base_datos = BaseDeDatos()
        try:
            cls.base_datos.inicializar()
        except mysql.connector.Error as error:
            raise unittest.SkipTest(f"MariaDB de XAMPP no está disponible: {error}")
        cls.servicio = TiendaServicio(cls.base_datos)
        cls.marca = uuid4().hex

    @classmethod
    def tearDownClass(cls) -> None:
        conexion = cls.base_datos.conectar()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM detalles_pedido WHERE pedido_id IN "
                    "(SELECT id FROM pedidos WHERE cliente_id IN "
                    "(SELECT id FROM clientes WHERE correo LIKE %s))",
                    (f"prueba-{cls.marca}-%@example.invalid",),
                )
                cursor.execute(
                    "DELETE FROM pedidos WHERE cliente_id IN "
                    "(SELECT id FROM clientes WHERE correo LIKE %s)",
                    (f"prueba-{cls.marca}-%@example.invalid",),
                )
                cursor.execute(
                    "DELETE FROM productos WHERE nombre LIKE %s",
                    (f"PRUEBA-{cls.marca}-%",),
                )
                cursor.execute(
                    "DELETE FROM clientes WHERE correo LIKE %s",
                    (f"prueba-{cls.marca}-%@example.invalid",),
                )
            conexion.commit()
        finally:
            conexion.close()

    def test_conexion_y_flujo_de_compra_persisten_datos(self) -> None:
        self.assertTrue(self.base_datos.probar_conexion())
        cliente = self.servicio.registrar_cliente(
            Cliente("Cliente de prueba", f"prueba-{self.marca}-1@example.invalid")
        )
        producto = self.servicio.registrar_producto(
            Producto(f"PRUEBA-{self.marca}-PRODUCTO", "Prueba", 15990, 5)
        )
        pedido = self.servicio.crear_pedido(cliente)
        detalle = self.servicio.agregar_producto(pedido, producto, 2)

        self.assertEqual(detalle.subtotal_centavos, 31980)
        self.assertEqual(pedido.total_centavos, 31980)
        self.assertEqual(producto.stock, 3)

        conexion = self.base_datos.conectar()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT total_centavos FROM pedidos WHERE id = %s", (pedido.id,)
                )
                total = cursor.fetchone()[0]
                cursor.execute(
                    "SELECT stock FROM productos WHERE id = %s", (producto.id,)
                )
                stock = cursor.fetchone()[0]
        finally:
            conexion.close()
        self.assertEqual(total, 31980)
        self.assertEqual(stock, 3)


if __name__ == "__main__":
    unittest.main()
