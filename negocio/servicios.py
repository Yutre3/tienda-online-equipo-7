"""Casos de uso y transacciones de la tienda en línea."""

from datetime import date
import re

import bcrypt

from auxiliares.validaciones import (
    validar_correo,
    validar_dato_obligatorio,
    validar_fecha_nacimiento,
    validar_genero,
    validar_rut,
)
from datos.conexion import transaccion_escritura
from datos.modelos import UsuarioModelo
from datos.repositorios import (
    RepositorioClientes,
    RepositorioPaises,
    RepositorioPedidos,
    RepositorioProductos,
    RepositorioUsuarios,
)
from negocio.entidades import (
    Cliente,
    DetallePedido,
    ErrorDominio,
    EstadoPedido,
    Pedido,
    Producto,
)
from negocio.negocio_usuario import crear_hash_contrasenia


_HASH_BCRYPT_FICTICIO = (
    b"$2b$12$/b1Q4Gffqego9nHl1WBd4eRNwFXk6hLFELK5/2MqK38UVGwBQnX/m"
)


def _preparar_hash_bcrypt(hash_guardado: object) -> tuple[bytes, bool]:
    if not isinstance(hash_guardado, str) or not re.fullmatch(
        r"\$2[aby]\$(?:0[4-9]|[12]\d|3[01])\$"
        r"[./A-Za-z0-9]{21}[.Oeu][./A-Za-z0-9]{31}",
        hash_guardado,
    ):
        return _HASH_BCRYPT_FICTICIO, False
    return hash_guardado.encode("ascii"), True


def _id_requerido(identificador: int | None, tipo: str) -> int:
    if identificador is None:
        raise ErrorDominio(f"El {tipo} todavía no ha sido guardado.")
    return identificador


class TiendaServicio:
    """Fachada de negocio utilizada por la presentación."""

    def __init__(
        self,
        clientes: RepositorioClientes | None = None,
        productos: RepositorioProductos | None = None,
        pedidos: RepositorioPedidos | None = None,
        paises: RepositorioPaises | None = None,
        usuarios: RepositorioUsuarios | None = None,
    ) -> None:
        self._clientes = clientes or RepositorioClientes()
        self._productos = productos or RepositorioProductos()
        self._pedidos = pedidos or RepositorioPedidos()
        self._paises = paises or RepositorioPaises()
        self._usuarios = usuarios or RepositorioUsuarios()

    def listar_paises(self, nombre: str = ""):
        return self._paises.buscar(nombre) if nombre.strip() else self._paises.listar_habilitados()

    def registrar_usuario(
        self,
        *,
        rut: str,
        nombre: str,
        apellido: str,
        correo: str,
        pais_id: int,
        fecha_nacimiento: date | str,
        genero: int | str,
        contrasenia: str,
    ) -> UsuarioModelo:
        pais = self._paises.obtener(pais_id)
        usuario = UsuarioModelo()
        usuario.rut = validar_rut(rut)
        usuario.nombre = validar_dato_obligatorio(nombre).title()
        usuario.apellido = validar_dato_obligatorio(apellido).title()
        usuario.correo = validar_correo(correo)
        usuario.pais = pais
        usuario.fecha_nacimiento = self._fecha_nacimiento(fecha_nacimiento)
        usuario.genero = validar_genero(genero)
        usuario.habilitado = True
        usuario.password = crear_hash_contrasenia(contrasenia)
        return self._usuarios.guardar(usuario)

    def listar_usuarios(self, habilitado: bool | None = True) -> list[UsuarioModelo]:
        return self._usuarios.listar(habilitado)

    def buscar_usuario_rut(self, rut: str) -> UsuarioModelo:
        usuario = self._usuarios.obtener_por_rut(validar_rut(rut))
        if usuario is None:
            raise ErrorDominio("No existe el usuario solicitado.")
        return usuario

    def buscar_usuario_correo(self, correo: str) -> UsuarioModelo:
        usuario = self._usuarios.obtener_por_correo(validar_correo(correo))
        if usuario is None:
            raise ErrorDominio("No existe el usuario solicitado.")
        return usuario

    def autenticar_usuario(
        self, correo: str, contrasenia: str
    ) -> UsuarioModelo:
        mensaje = "No fue posible iniciar sesión con las credenciales ingresadas."
        usuario = None
        try:
            usuario = self.buscar_usuario_correo(correo)
        except (ErrorDominio, ValueError):
            pass

        hash_guardado = getattr(usuario, "password", None)
        hash_bcrypt, hash_valido = _preparar_hash_bcrypt(hash_guardado)

        try:
            coincide = bcrypt.checkpw(
                contrasenia.encode("utf-8"), hash_bcrypt
            )
        except (AttributeError, ValueError):
            coincide = False
        if (
            usuario is None
            or not usuario.habilitado
            or not hash_valido
            or not coincide
        ):
            raise ErrorDominio(mensaje)
        return usuario

    def estado_acceso_usuarios(self) -> str:
        """Resume si la instalación puede presentar el formulario de acceso."""
        usuarios = self.listar_usuarios(None)
        if not usuarios:
            return "sin_usuarios"
        habilitados = [usuario for usuario in usuarios if usuario.habilitado]
        if not habilitados:
            return "sin_habilitados"
        if any(
            _preparar_hash_bcrypt(usuario.password)[1]
            for usuario in habilitados
        ):
            return "disponible"
        return "sin_password_valido"

    def cambiar_contrasenia_usuario_existente(
        self, correo: str, contrasenia: str
    ) -> UsuarioModelo:
        """Reemplaza solo el hash de una cuenta ya existente."""
        usuario = self.buscar_usuario_correo(correo)
        usuario.password = crear_hash_contrasenia(contrasenia)
        return self._usuarios.guardar(usuario)

    def actualizar_usuario(
        self,
        rut_actual: str,
        *,
        rut: str | None = None,
        nombre: str | None = None,
        apellido: str | None = None,
        correo: str | None = None,
        pais_id: int | None = None,
        fecha_nacimiento: date | str | None = None,
        genero: int | str | None = None,
    ) -> UsuarioModelo:
        usuario = self.buscar_usuario_rut(rut_actual)
        if rut is not None:
            usuario.rut = validar_rut(rut)
        if nombre is not None:
            usuario.nombre = validar_dato_obligatorio(nombre).title()
        if apellido is not None:
            usuario.apellido = validar_dato_obligatorio(apellido).title()
        if correo is not None:
            usuario.correo = validar_correo(correo)
        if pais_id is not None:
            usuario.pais = self._paises.obtener(pais_id)
        if fecha_nacimiento is not None:
            usuario.fecha_nacimiento = self._fecha_nacimiento(fecha_nacimiento)
        if genero is not None:
            usuario.genero = validar_genero(genero)
        return self._usuarios.guardar(usuario)

    def deshabilitar_usuario(self, rut: str) -> UsuarioModelo:
        usuario = self.buscar_usuario_rut(rut)
        usuario.habilitado = False
        return self._usuarios.guardar(usuario)

    @staticmethod
    def _fecha_nacimiento(valor: date | str) -> date:
        if isinstance(valor, date):
            return valor
        return validar_fecha_nacimiento(valor)

    def registrar_cliente(self, cliente: Cliente) -> Cliente:
        return self._clientes.crear(cliente)

    def obtener_cliente(self, identificador: int) -> Cliente:
        return self._clientes.obtener(identificador)

    def listar_clientes(self) -> list[Cliente]:
        return self._clientes.listar()

    def actualizar_cliente(self, cliente: Cliente) -> Cliente:
        return self._clientes.actualizar(cliente)

    def eliminar_cliente(self, identificador: int | None) -> None:
        self._clientes.eliminar(_id_requerido(identificador, "cliente"))

    def registrar_producto(self, producto: Producto) -> Producto:
        return self._productos.crear(producto)

    def obtener_producto(self, identificador: int) -> Producto:
        return self._productos.obtener(identificador)

    def listar_productos(self) -> list[Producto]:
        return self._productos.listar()

    def actualizar_producto(self, producto: Producto) -> Producto:
        return self._productos.actualizar(producto)

    def eliminar_producto(self, identificador: int | None) -> None:
        self._productos.eliminar(_id_requerido(identificador, "producto"))

    def crear_pedido(self, cliente_id: int) -> Pedido:
        cliente = self._clientes.obtener(cliente_id)
        return self._pedidos.crear(Pedido(cliente))

    def obtener_pedido(self, identificador: int) -> Pedido:
        return self._pedidos.obtener(identificador)

    def listar_pedidos(self) -> list[Pedido]:
        return self._pedidos.listar()

    def agregar_producto(
        self, pedido_id: int, producto_id: int, cantidad: int
    ) -> Pedido:
        with transaccion_escritura():
            pedido = self._pedidos.obtener_para_actualizar(pedido_id)
            if pedido.estado is not EstadoPedido.CREADO:
                raise ErrorDominio(
                    "Solo se pueden modificar pedidos en estado CREADO."
                )
            producto = self._productos.obtener(producto_id)
            detalle = DetallePedido(producto, cantidad)
            self._productos.descontar_stock(producto_id, cantidad)
            self._pedidos.guardar_detalle(pedido_id, detalle)
        return self._pedidos.obtener(pedido_id)

    def quitar_producto(self, pedido_id: int, producto_id: int) -> Pedido:
        with transaccion_escritura():
            pedido = self._pedidos.obtener_para_actualizar(pedido_id)
            if pedido.estado is not EstadoPedido.CREADO:
                raise ErrorDominio(
                    "Solo se pueden modificar pedidos en estado CREADO."
                )
            detalle = self._pedidos.eliminar_detalle(pedido_id, producto_id)
            self._productos.reponer_stock(producto_id, detalle.cantidad)
        return self._pedidos.obtener(pedido_id)

    def confirmar_pedido(self, pedido_id: int) -> Pedido:
        with transaccion_escritura():
            pedido = self._pedidos.obtener_para_actualizar(pedido_id)
            pedido.cambiar_estado(EstadoPedido.CONFIRMADO)
            self._pedidos.cambiar_estado(pedido_id, pedido.estado)
        return self._pedidos.obtener(pedido_id)

    def cancelar_pedido(self, pedido_id: int) -> Pedido:
        with transaccion_escritura():
            pedido = self._pedidos.obtener_para_actualizar(pedido_id)
            pedido.cambiar_estado(EstadoPedido.CANCELADO)
            self._reponer_detalles(pedido)
            self._pedidos.cambiar_estado(pedido_id, pedido.estado)
        return self._pedidos.obtener(pedido_id)

    def eliminar_pedido(self, pedido_id: int) -> None:
        with transaccion_escritura():
            pedido = self._pedidos.obtener_para_actualizar(pedido_id)
            if pedido.estado is not EstadoPedido.CANCELADO:
                self._reponer_detalles(pedido)
            self._pedidos.eliminar(pedido_id)

    def _reponer_detalles(self, pedido: Pedido) -> None:
        for detalle in pedido.detalles:
            producto_id = _id_requerido(detalle.producto.id, "producto")
            self._productos.reponer_stock(producto_id, detalle.cantidad)
