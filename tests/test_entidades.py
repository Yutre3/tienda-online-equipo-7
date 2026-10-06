import unittest

from negocio.entidades import Cliente, DetallePedido, Pedido, Producto


class EntidadesTest(unittest.TestCase):
    def test_cliente_normaliza_correo(self) -> None:
        cliente = Cliente("Ana", " ANA@EJEMPLO.CL ")
        self.assertEqual(cliente.correo, "ana@ejemplo.cl")

    def test_producto_no_permite_stock_negativo(self) -> None:
        with self.assertRaises(ValueError):
            Producto("Teclado", "", 1000, -1)

    def test_pedido_calcula_total_y_compone_detalle(self) -> None:
        cliente = Cliente("Ana", "ana@ejemplo.cl", 1)
        producto = Producto("Teclado", "Mecánico", 150000, 3, 1)
        pedido = Pedido(cliente, identificador=1)
        detalle = DetallePedido(producto, 2)
        pedido.agregar_detalle(detalle)
        self.assertEqual(pedido.total_centavos, 300000)
        self.assertEqual(pedido.detalles, (detalle,))


if __name__ == "__main__":
    unittest.main()
