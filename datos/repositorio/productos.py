"""Funciones Peewee para persistir productos e inventario."""

from datetime import datetime

from peewee import IntegrityError

from datos.modelos import ProductoModelo
from datos.repositorio.clientes import _id_requerido
from negocio.entidades import ErrorDominio, Producto


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


def guardar_producto(producto: Producto) -> Producto:
    modelo = ProductoModelo(
        sku=producto.sku,
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio_centavos=producto.precio_centavos,
        stock=producto.stock,
    )
    try:
        modelo.save()
    except IntegrityError as error:
        raise ErrorDominio("Ya existe un producto con ese SKU.") from error
    producto.asignar_id(modelo.id)
    producto.creado_en = modelo.creado_en
    return producto


def obtener_producto(identificador: int) -> Producto:
    modelo = ProductoModelo.get_or_none(ProductoModelo.id == identificador)
    if modelo is None:
        raise ErrorDominio("No existe el producto solicitado.")
    return _producto_entidad(modelo)


def listar_productos() -> list[Producto]:
    return [
        _producto_entidad(modelo)
        for modelo in ProductoModelo.select().order_by(ProductoModelo.id)
    ]


def modificar_producto(producto: Producto) -> Producto:
    identificador = _id_requerido(producto.id, "producto")
    modelo = ProductoModelo.get_or_none(ProductoModelo.id == identificador)
    if modelo is None:
        raise ErrorDominio("No existe el producto solicitado.")
    modelo.sku = producto.sku
    modelo.nombre = producto.nombre
    modelo.descripcion = producto.descripcion
    modelo.precio_centavos = producto.precio_centavos
    modelo.stock = producto.stock
    modelo.actualizado_en = datetime.now()
    try:
        modelo.save()
    except IntegrityError as error:
        raise ErrorDominio("Ya existe un producto con ese SKU.") from error
    return producto


def eliminar_producto(identificador: int) -> None:
    try:
        filas = (
            ProductoModelo.delete()
            .where(ProductoModelo.id == identificador)
            .execute()
        )
    except IntegrityError as error:
        raise ErrorDominio(
            "No se puede eliminar un producto incluido en pedidos."
        ) from error
    if filas != 1:
        raise ErrorDominio("No existe el producto solicitado.")


def descontar_stock(identificador: int, cantidad: int) -> None:
    filas = (
        ProductoModelo.update(stock=ProductoModelo.stock - cantidad)
        .where(
            (ProductoModelo.id == identificador)
            & (ProductoModelo.stock >= cantidad)
        )
        .execute()
    )
    if filas != 1:
        raise ErrorDominio("No existe stock suficiente para el producto.")


def reponer_stock(identificador: int, cantidad: int) -> None:
    filas = (
        ProductoModelo.update(stock=ProductoModelo.stock + cantidad)
        .where(ProductoModelo.id == identificador)
        .execute()
    )
    if filas != 1:
        raise ErrorDominio("No existe el producto solicitado.")
