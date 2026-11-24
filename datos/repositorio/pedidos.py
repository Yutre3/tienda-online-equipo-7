"""Funciones Peewee para persistir pedidos y sus detalles."""

from datetime import datetime

from peewee import IntegrityError, MySQLDatabase

from datos.modelos import (
    ClienteModelo,
    DetallePedidoModelo,
    PedidoModelo,
    ProductoModelo,
)
from datos.repositorio.clientes import _cliente_entidad, _id_requerido
from datos.repositorio.productos import _producto_entidad
from negocio.entidades import DetallePedido, ErrorDominio, EstadoPedido, Pedido


def guardar_pedido(pedido: Pedido) -> Pedido:
    cliente_id = _id_requerido(pedido.cliente.id, "cliente")
    modelo = PedidoModelo(cliente=cliente_id, estado=pedido.estado.value)
    try:
        modelo.save()
    except IntegrityError as error:
        raise ErrorDominio(
            "No fue posible asociar el pedido con el cliente."
        ) from error
    pedido.asignar_id(modelo.id)
    pedido.creado_en = modelo.creado_en
    return pedido


def _consulta_pedido(identificador: int):
    return (
        PedidoModelo.select(PedidoModelo, ClienteModelo)
        .join(ClienteModelo)
        .where(PedidoModelo.id == identificador)
    )


def _detalle_entidad(modelo: DetallePedidoModelo) -> DetallePedido:
    return DetallePedido(
        _producto_entidad(modelo.producto),
        modelo.cantidad,
        modelo.id,
        modelo.precio_unitario_centavos,
    )


def _pedido_entidad(modelo: PedidoModelo) -> Pedido:
    detalles = [
        _detalle_entidad(detalle)
        for detalle in (
            DetallePedidoModelo.select(DetallePedidoModelo, ProductoModelo)
            .join(ProductoModelo)
            .where(DetallePedidoModelo.pedido == modelo.id)
            .order_by(DetallePedidoModelo.id)
        )
    ]
    return Pedido(
        _cliente_entidad(modelo.cliente),
        modelo.estado,
        detalles,
        modelo.id,
        modelo.creado_en,
    )


def obtener_pedido(identificador: int) -> Pedido:
    modelo = _consulta_pedido(identificador).get_or_none()
    if modelo is None:
        raise ErrorDominio("No existe el pedido solicitado.")
    return _pedido_entidad(modelo)


def obtener_pedido_para_actualizar(identificador: int) -> Pedido:
    consulta = _consulta_pedido(identificador)
    from datos.conexion import base_datos_proxy

    if isinstance(base_datos_proxy.obj, MySQLDatabase):
        consulta = consulta.for_update()
    modelo = consulta.get_or_none()
    if modelo is None:
        raise ErrorDominio("No existe el pedido solicitado.")
    return _pedido_entidad(modelo)


def listar_pedidos() -> list[Pedido]:
    return [
        obtener_pedido(modelo.id)
        for modelo in PedidoModelo.select().order_by(PedidoModelo.id)
    ]


def guardar_detalle(
    pedido_id: int | None, detalle: DetallePedido
) -> DetallePedido:
    pedido_id = _id_requerido(pedido_id, "pedido")
    producto_id = _id_requerido(detalle.producto.id, "producto")
    existente = DetallePedidoModelo.get_or_none(
        (DetallePedidoModelo.pedido == pedido_id)
        & (DetallePedidoModelo.producto == producto_id)
    )
    if existente is None:
        modelo = DetallePedidoModelo(
            pedido=pedido_id,
            producto=producto_id,
            cantidad=detalle.cantidad,
            precio_unitario_centavos=detalle.precio_unitario_centavos,
            subtotal_centavos=detalle.subtotal_centavos,
        )
        modelo.save()
        detalle.asignar_id(modelo.id)
    else:
        existente.cantidad += detalle.cantidad
        existente.subtotal_centavos = (
            existente.cantidad * existente.precio_unitario_centavos
        )
        existente.save()
        if detalle.id is None:
            detalle.asignar_id(existente.id)
    recalcular_total(pedido_id)
    return detalle


def eliminar_detalle(pedido_id: int, producto_id: int) -> DetallePedido:
    modelo = (
        DetallePedidoModelo.select(DetallePedidoModelo, ProductoModelo)
        .join(ProductoModelo)
        .where(
            (DetallePedidoModelo.pedido == pedido_id)
            & (DetallePedidoModelo.producto == producto_id)
        )
        .get_or_none()
    )
    if modelo is None:
        raise ErrorDominio("El producto no pertenece al pedido.")
    detalle = _detalle_entidad(modelo)
    modelo.delete_instance()
    recalcular_total(pedido_id)
    return detalle


def cambiar_estado_pedido(pedido_id: int, estado: EstadoPedido) -> None:
    modelo = PedidoModelo.get_or_none(PedidoModelo.id == pedido_id)
    if modelo is None:
        raise ErrorDominio("No existe el pedido solicitado.")
    modelo.estado = estado.value
    modelo.actualizado_en = datetime.now()
    modelo.save()


def eliminar_pedido(pedido_id: int) -> None:
    filas = PedidoModelo.delete().where(PedidoModelo.id == pedido_id).execute()
    if filas != 1:
        raise ErrorDominio("No existe el pedido solicitado.")


def recalcular_total(pedido_id: int) -> int:
    total = sum(
        detalle.subtotal_centavos
        for detalle in DetallePedidoModelo.select().where(
            DetallePedidoModelo.pedido == pedido_id
        )
    )
    modelo = PedidoModelo.get_or_none(PedidoModelo.id == pedido_id)
    if modelo is None:
        raise ErrorDominio("No existe el pedido solicitado.")
    modelo.total_centavos = total
    modelo.actualizado_en = datetime.now()
    modelo.save()
    return total
