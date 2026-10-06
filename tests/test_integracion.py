from uuid import uuid4
import unittest

import mysql.connector

from datos.conexion import BaseDeDatos
from datos.repositorios import TiendaRepositorio
from negocio.entidades import Cliente, Producto
from negocio.servicios import TiendaServicio


class IntegracionTiendaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base = BaseDeDatos()
        try:
            cls.base.inicializar()
        except mysql.connector.Error as error:
            raise unittest.SkipTest(f"MariaDB no está disponible: {error}")
        cls.servicio = TiendaServicio(TiendaRepositorio(cls.base))
        cls.marca = uuid4().hex

    @classmethod
    def tearDownClass(cls) -> None:
        conexion = cls.base.conectar()
        try:
            with conexion.cursor() as cursor:
                correo = f"prueba-{cls.marca}@example.invalid"
                cursor.execute(
                    "DELETE FROM detalles_pedido WHERE pedido_id IN "
                    "(SELECT id FROM pedidos WHERE cliente_id IN "
                    "(SELECT id FROM clientes WHERE correo = %s))", (correo,)
                )
                cursor.execute(
                    "DELETE FROM pedidos WHERE cliente_id IN "
                    "(SELECT id FROM clientes WHERE correo = %s)", (correo,)
                )
                cursor.execute("DELETE FROM productos WHERE nombre = %s",
                               (f"PRUEBA-{cls.marca}",))
                cursor.execute("DELETE FROM clientes WHERE correo = %s", (correo,))
            conexion.commit()
        finally:
            conexion.close()

    def test_flujo_de_compra_persiste_datos(self) -> None:
        cliente = self.servicio.registrar_cliente(
            Cliente("Cliente de prueba", f"prueba-{self.marca}@example.invalid")
        )
        producto = self.servicio.registrar_producto(
            Producto(f"PRUEBA-{self.marca}", "Prueba", 15990, 5)
        )
        pedido = self.servicio.crear_pedido(cliente)
        detalle = self.servicio.agregar_producto(pedido, producto, 2)
        self.assertEqual(detalle.subtotal_centavos, 31980)
        self.assertEqual(pedido.total_centavos, 31980)
        self.assertEqual(producto.stock, 3)


if __name__ == "__main__":
    unittest.main()
