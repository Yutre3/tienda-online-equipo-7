from datetime import date
import inspect

import bcrypt

from datos.modelos import (
    ClienteModelo,
    PaisModelo,
    PedidoModelo,
    ProductoModelo,
    UsuarioModelo,
)
from datos.repositorio import clientes, paises, pedidos, productos, usuarios
from negocio import Cliente, DetallePedido, Pedido, Producto


def _crear_pais() -> PaisModelo:
    pais = PaisModelo(
        pais="Chile",
        nacionalidad="Chilena",
        iso2="CL",
        iso3="CHL",
        habilitado=True,
    )
    pais.save()
    return pais


def _crear_usuario(pais: PaisModelo) -> UsuarioModelo:
    return UsuarioModelo(
        rut="12345678-5",
        nombre="Ana",
        apellido="Pérez",
        correo="ana@ejemplo.cl",
        pais=pais,
        fecha_nacimiento=date(1990, 5, 10),
        genero=2,
        habilitado=True,
        password=bcrypt.hashpw(b"Segura1!", bcrypt.gensalt()).decode("ascii"),
    )


def test_repositorios_obligatorios_exponen_funciones() -> None:
    funciones = (
        clientes.guardar_cliente,
        clientes.listar_clientes,
        clientes.obtener_cliente,
        clientes.modificar_cliente,
        clientes.eliminar_cliente,
        productos.guardar_producto,
        productos.listar_productos,
        productos.obtener_producto,
        productos.modificar_producto,
        productos.eliminar_producto,
        pedidos.guardar_pedido,
        pedidos.listar_pedidos,
        pedidos.obtener_pedido,
        pedidos.cambiar_estado_pedido,
        pedidos.eliminar_pedido,
        usuarios.guardar_usuario,
        usuarios.guardar_primer_usuario,
        usuarios.actualizar_password_usuario,
        usuarios.listado_usuarios,
        usuarios.obtener_usuario_rut,
        usuarios.obtener_usuario_correo,
        paises.listado_paises,
        paises.buscar_paises,
        paises.obtener_pais_id,
    )

    assert all(inspect.isfunction(funcion) for funcion in funciones)


def test_funciones_crud_clientes_productos_y_pedidos(base_pruebas) -> None:
    cliente = clientes.guardar_cliente(Cliente("Ana", "ana@ejemplo.cl"))
    producto = productos.guardar_producto(
        Producto("TEC-1", "Teclado", "Mecánico", 3999000, 8)
    )
    pedido = pedidos.guardar_pedido(Pedido(cliente))
    pedidos.guardar_detalle(pedido.id, DetallePedido(producto, 2))

    cliente.nombre = "Ana María"
    clientes.modificar_cliente(cliente)
    producto.stock = 10
    productos.modificar_producto(producto)

    recuperado = pedidos.obtener_pedido(pedido.id)
    assert [actual.nombre for actual in clientes.listar_clientes()] == [
        "Ana María"
    ]
    assert productos.obtener_producto(producto.id).stock == 10
    assert recuperado.detalles[0].cantidad == 2
    assert recuperado.total_centavos == 7998000

    pedidos.eliminar_pedido(pedido.id)
    productos.eliminar_producto(producto.id)
    clientes.eliminar_cliente(cliente.id)
    assert pedidos.listar_pedidos() == []
    assert productos.listar_productos() == []
    assert clientes.listar_clientes() == []


def test_funciones_de_usuarios_y_paises_buscan_modifican_y_deshabilitan(
    base_pruebas,
) -> None:
    pais = _crear_pais()
    usuario = usuarios.guardar_usuario(_crear_usuario(pais))

    assert paises.listado_paises() == [pais]
    assert paises.buscar_paises("hil") == [pais]
    assert paises.obtener_pais_id(pais.id_pais) == pais
    assert usuarios.obtener_usuario_rut(usuario.rut) == usuario
    assert usuarios.obtener_usuario_correo(usuario.correo) == usuario

    usuario.nombre = "Ana María"
    usuario.habilitado = False
    usuarios.guardar_usuario(usuario)

    assert usuarios.listado_usuarios_habilitados() == []
    assert usuarios.listado_usuarios_deshabilitados()[0].nombre == "Ana María"
    assert usuarios.listado_usuarios()[0].habilitado is False


def test_altas_funcionales_invocan_save_de_los_modelos(
    base_pruebas, monkeypatch
) -> None:
    llamadas = {"cliente": 0, "producto": 0, "pedido": 0, "usuario": 0}

    def observar(modelo, clave: str) -> None:
        original = modelo.save

        def guardar(instancia, *args, **kwargs):
            llamadas[clave] += 1
            return original(instancia, *args, **kwargs)

        monkeypatch.setattr(modelo, "save", guardar)

    observar(ClienteModelo, "cliente")
    observar(ProductoModelo, "producto")
    observar(PedidoModelo, "pedido")
    observar(UsuarioModelo, "usuario")

    pais = _crear_pais()
    cliente = clientes.guardar_cliente(Cliente("Ana", "ana@ejemplo.cl"))
    productos.guardar_producto(Producto("TEC-1", "Teclado", "", 1000, 2))
    pedidos.guardar_pedido(Pedido(cliente))
    usuarios.guardar_usuario(_crear_usuario(pais))

    assert llamadas == {"cliente": 1, "producto": 1, "pedido": 1, "usuario": 1}
