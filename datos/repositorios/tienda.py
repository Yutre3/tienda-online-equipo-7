"""Operaciones de persistencia expresadas con Peewee."""

from datetime import datetime

from peewee import IntegrityError, MySQLDatabase

from datos.modelos import (
    ClienteModelo,
    DetallePedidoModelo,
    PedidoModelo,
    ProductoModelo,
)
from negocio.entidades import (
    Cliente,
    DetallePedido,
    ErrorDominio,
    EstadoPedido,
    Pedido,
    Producto,
)


def _id_requerido(identificador: int | None, tipo: str) -> int:
    if identificador is None:
        raise ErrorDominio(f"El {tipo} todavía no ha sido guardado.")
    return identificador


def _cliente_entidad(modelo: ClienteModelo) -> Cliente:
    return Cliente(modelo.nombre, modelo.correo, modelo.id, modelo.creado_en)


def _producto_entidad(modelo: ProductoModelo) -> Producto:
    return Producto(
        modelo.sku,
        modelo.nombre,
        modelo.descripcion,
        modelo.precio_centavos,
        modelo.stock,
        modelo.id,
        modelo.creado_en,
    )


class RepositorioClientes:
    def crear(self, cliente: Cliente) -> Cliente:
        try:
            modelo = ClienteModelo.create(nombre=cliente.nombre, correo=cliente.correo)
        except IntegrityError as error:
            raise ErrorDominio("Ya existe un cliente con ese correo.") from error
        cliente.asignar_id(modelo.id)
        cliente.creado_en = modelo.creado_en
        return cliente

    def obtener(self, identificador: int) -> Cliente:
        modelo = ClienteModelo.get_or_none(ClienteModelo.id == identificador)
        if modelo is None:
            raise ErrorDominio("No existe el cliente solicitado.")
        return _cliente_entidad(modelo)

    def listar(self) -> list[Cliente]:
        return [_cliente_entidad(modelo) for modelo in ClienteModelo.select().order_by(ClienteModelo.id)]

    def actualizar(self, cliente: Cliente) -> Cliente:
        identificador = _id_requerido(cliente.id, "cliente")
        try:
            filas = (ClienteModelo.update(nombre=cliente.nombre, correo=cliente.correo)
                     .where(ClienteModelo.id == identificador).execute())
        except IntegrityError as error:
            raise ErrorDominio("Ya existe un cliente con ese correo.") from error
        if filas != 1:
            raise ErrorDominio("No existe el cliente solicitado.")
        return cliente

    def eliminar(self, identificador: int) -> None:
        try:
            filas = ClienteModelo.delete().where(ClienteModelo.id == identificador).execute()
        except IntegrityError as error:
            raise ErrorDominio("No se puede eliminar un cliente que tiene pedidos.") from error
        if filas != 1:
            raise ErrorDominio("No existe el cliente solicitado.")


class RepositorioProductos:
    def crear(self, producto: Producto) -> Producto:
        try:
            modelo = ProductoModelo.create(
                sku=producto.sku,
                nombre=producto.nombre,
                descripcion=producto.descripcion,
                precio_centavos=producto.precio_centavos,
                stock=producto.stock,
            )
        except IntegrityError as error:
            raise ErrorDominio("Ya existe un producto con ese SKU.") from error
        producto.asignar_id(modelo.id)
        producto.creado_en = modelo.creado_en
        return producto

    def obtener(self, identificador: int) -> Producto:
        modelo = ProductoModelo.get_or_none(ProductoModelo.id == identificador)
        if modelo is None:
            raise ErrorDominio("No existe el producto solicitado.")
        return _producto_entidad(modelo)

    def listar(self) -> list[Producto]:
        return [_producto_entidad(modelo) for modelo in ProductoModelo.select().order_by(ProductoModelo.id)]

    def actualizar(self, producto: Producto) -> Producto:
        identificador = _id_requerido(producto.id, "producto")
        try:
            filas = (ProductoModelo.update(
                sku=producto.sku,
                nombre=producto.nombre,
                descripcion=producto.descripcion,
                precio_centavos=producto.precio_centavos,
                stock=producto.stock,
                actualizado_en=datetime.now(),
            ).where(ProductoModelo.id == identificador).execute())
        except IntegrityError as error:
            raise ErrorDominio("Ya existe un producto con ese SKU.") from error
        if filas != 1:
            raise ErrorDominio("No existe el producto solicitado.")
        return producto

    def eliminar(self, identificador: int) -> None:
        try:
            filas = ProductoModelo.delete().where(ProductoModelo.id == identificador).execute()
        except IntegrityError as error:
            raise ErrorDominio("No se puede eliminar un producto incluido en pedidos.") from error
        if filas != 1:
            raise ErrorDominio("No existe el producto solicitado.")

    def descontar_stock(self, identificador: int, cantidad: int) -> None:
        filas = (ProductoModelo.update(stock=ProductoModelo.stock - cantidad)
                 .where(
                     (ProductoModelo.id == identificador)
                     & (ProductoModelo.stock >= cantidad)
                 ).execute())
        if filas != 1:
            raise ErrorDominio("No existe stock suficiente para el producto.")

    def reponer_stock(self, identificador: int, cantidad: int) -> None:
        filas = (ProductoModelo.update(stock=ProductoModelo.stock + cantidad)
                 .where(ProductoModelo.id == identificador).execute())
        if filas != 1:
            raise ErrorDominio("No existe el producto solicitado.")


class RepositorioPedidos:
    def crear(self, pedido: Pedido) -> Pedido:
        cliente_id = _id_requerido(pedido.cliente.id, "cliente")
        try:
            modelo = PedidoModelo.create(cliente=cliente_id, estado=pedido.estado.value)
        except IntegrityError as error:
            raise ErrorDominio("No fue posible asociar el pedido con el cliente.") from error
        pedido.asignar_id(modelo.id)
        pedido.creado_en = modelo.creado_en
        return pedido

    def obtener(self, identificador: int) -> Pedido:
        modelo = self._consulta_pedido(identificador).get_or_none()
        if modelo is None:
            raise ErrorDominio("No existe el pedido solicitado.")
        return self._pedido_entidad(modelo)

    def obtener_para_actualizar(self, identificador: int) -> Pedido:
        consulta = self._consulta_pedido(identificador)
        from datos.conexion import base_datos_proxy

        if isinstance(base_datos_proxy.obj, MySQLDatabase):
            consulta = consulta.for_update()
        modelo = consulta.get_or_none()
        if modelo is None:
            raise ErrorDominio("No existe el pedido solicitado.")
        return self._pedido_entidad(modelo)

    @staticmethod
    def _consulta_pedido(identificador: int):
        return (PedidoModelo.select(PedidoModelo, ClienteModelo)
                .join(ClienteModelo)
                .where(PedidoModelo.id == identificador))

    def _pedido_entidad(self, modelo: PedidoModelo) -> Pedido:
        cliente = _cliente_entidad(modelo.cliente)
        detalles = [self._detalle_entidad(detalle) for detalle in (
            DetallePedidoModelo.select(DetallePedidoModelo, ProductoModelo)
            .join(ProductoModelo)
            .where(DetallePedidoModelo.pedido == modelo.id)
            .order_by(DetallePedidoModelo.id)
        )]
        return Pedido(cliente, modelo.estado, detalles, modelo.id, modelo.creado_en)

    def listar(self) -> list[Pedido]:
        return [self.obtener(modelo.id) for modelo in PedidoModelo.select().order_by(PedidoModelo.id)]

    def guardar_detalle(self, pedido_id: int | None, detalle: DetallePedido) -> DetallePedido:
        pedido_id = _id_requerido(pedido_id, "pedido")
        producto_id = _id_requerido(detalle.producto.id, "producto")
        existente = DetallePedidoModelo.get_or_none(
            (DetallePedidoModelo.pedido == pedido_id)
            & (DetallePedidoModelo.producto == producto_id)
        )
        if existente is None:
            modelo = DetallePedidoModelo.create(
                pedido=pedido_id,
                producto=producto_id,
                cantidad=detalle.cantidad,
                precio_unitario_centavos=detalle.precio_unitario_centavos,
                subtotal_centavos=detalle.subtotal_centavos,
            )
            detalle.asignar_id(modelo.id)
        else:
            existente.cantidad += detalle.cantidad
            existente.subtotal_centavos = (
                existente.cantidad * existente.precio_unitario_centavos
            )
            existente.save()
            if detalle.id is None:
                detalle.asignar_id(existente.id)
        self.recalcular_total(pedido_id)
        return detalle

    def eliminar_detalle(self, pedido_id: int, producto_id: int) -> DetallePedido:
        modelo = (DetallePedidoModelo.select(DetallePedidoModelo, ProductoModelo)
                  .join(ProductoModelo)
                  .where(
                      (DetallePedidoModelo.pedido == pedido_id)
                      & (DetallePedidoModelo.producto == producto_id)
                  ).get_or_none())
        if modelo is None:
            raise ErrorDominio("El producto no pertenece al pedido.")
        detalle = self._detalle_entidad(modelo)
        modelo.delete_instance()
        self.recalcular_total(pedido_id)
        return detalle

    def cambiar_estado(self, pedido_id: int, estado: EstadoPedido) -> None:
        filas = (PedidoModelo.update(estado=estado.value, actualizado_en=datetime.now())
                 .where(PedidoModelo.id == pedido_id).execute())
        if filas != 1:
            raise ErrorDominio("No existe el pedido solicitado.")

    def eliminar(self, pedido_id: int) -> None:
        filas = PedidoModelo.delete().where(PedidoModelo.id == pedido_id).execute()
        if filas != 1:
            raise ErrorDominio("No existe el pedido solicitado.")

    def recalcular_total(self, pedido_id: int) -> int:
        total = sum(
            detalle.subtotal_centavos
            for detalle in DetallePedidoModelo.select().where(
                DetallePedidoModelo.pedido == pedido_id
            )
        )
        filas = (PedidoModelo.update(total_centavos=total, actualizado_en=datetime.now())
                 .where(PedidoModelo.id == pedido_id).execute())
        if filas != 1:
            raise ErrorDominio("No existe el pedido solicitado.")
        return total

    @staticmethod
    def _detalle_entidad(modelo: DetallePedidoModelo) -> DetallePedido:
        return DetallePedido(
            _producto_entidad(modelo.producto),
            modelo.cantidad,
            modelo.id,
            modelo.precio_unitario_centavos,
        )
