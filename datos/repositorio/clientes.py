"""Funciones Peewee para persistir clientes."""

from peewee import IntegrityError

from datos.modelos import ClienteModelo
from negocio.entidades import Cliente, ErrorDominio


def _id_requerido(identificador: int | None, tipo: str) -> int:
    if identificador is None:
        raise ErrorDominio(f"El {tipo} todavía no ha sido guardado.")
    return identificador


def _cliente_entidad(modelo: ClienteModelo) -> Cliente:
    return Cliente(modelo.nombre, modelo.correo, modelo.id, modelo.creado_en)


def guardar_cliente(cliente: Cliente) -> Cliente:
    modelo = ClienteModelo(nombre=cliente.nombre, correo=cliente.correo)
    try:
        modelo.save()
    except IntegrityError as error:
        raise ErrorDominio("Ya existe un cliente con ese correo.") from error
    cliente.asignar_id(modelo.id)
    cliente.creado_en = modelo.creado_en
    return cliente


def obtener_cliente(identificador: int) -> Cliente:
    modelo = ClienteModelo.get_or_none(ClienteModelo.id == identificador)
    if modelo is None:
        raise ErrorDominio("No existe el cliente solicitado.")
    return _cliente_entidad(modelo)


def listar_clientes() -> list[Cliente]:
    return [
        _cliente_entidad(modelo)
        for modelo in ClienteModelo.select().order_by(ClienteModelo.id)
    ]


def modificar_cliente(cliente: Cliente) -> Cliente:
    identificador = _id_requerido(cliente.id, "cliente")
    modelo = ClienteModelo.get_or_none(ClienteModelo.id == identificador)
    if modelo is None:
        raise ErrorDominio("No existe el cliente solicitado.")
    modelo.nombre = cliente.nombre
    modelo.correo = cliente.correo
    try:
        modelo.save()
    except IntegrityError as error:
        raise ErrorDominio("Ya existe un cliente con ese correo.") from error
    return cliente


def eliminar_cliente(identificador: int) -> None:
    try:
        filas = (
            ClienteModelo.delete()
            .where(ClienteModelo.id == identificador)
            .execute()
        )
    except IntegrityError as error:
        raise ErrorDominio(
            "No se puede eliminar un cliente que tiene pedidos."
        ) from error
    if filas != 1:
        raise ErrorDominio("No existe el cliente solicitado.")
