"""Entidades y reglas básicas del dominio de la tienda."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
import re


class ErrorDominio(ValueError):
    """Error esperado provocado por datos o acciones no válidas."""


class EstadoPedido(StrEnum):
    CREADO = "CREADO"
    CONFIRMADO = "CONFIRMADO"
    CANCELADO = "CANCELADO"


class Entidad:
    """Base común para entidades que pueden persistirse."""

    def __init__(self, identificador: int | None = None) -> None:
        if identificador is not None and (
            not isinstance(identificador, int)
            or isinstance(identificador, bool)
            or identificador <= 0
        ):
            raise ErrorDominio("El identificador debe ser un entero positivo.")
        self._id = identificador

    @property
    def id(self) -> int | None:
        return self._id

    def asignar_id(self, identificador: int) -> None:
        if self._id is not None:
            raise ErrorDominio("La entidad ya tiene un identificador.")
        if not isinstance(identificador, int) or identificador <= 0:
            raise ErrorDominio("El identificador debe ser un entero positivo.")
        self._id = identificador


class Cliente(Entidad):
    def __init__(self, nombre: str, correo: str, identificador: int | None = None,
                 creado_en: datetime | None = None) -> None:
        super().__init__(identificador)
        self.nombre = nombre
        self.correo = correo
        self.creado_en = creado_en

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        valor = str(valor).strip()
        if not valor:
            raise ErrorDominio("El nombre del cliente es obligatorio.")
        if len(valor) > 120:
            raise ErrorDominio("El nombre del cliente admite hasta 120 caracteres.")
        self._nombre = valor

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        valor = str(valor).strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", valor):
            raise ErrorDominio("El correo del cliente no es válido.")
        if len(valor) > 190:
            raise ErrorDominio("El correo admite hasta 190 caracteres.")
        self._correo = valor


class Producto(Entidad):
    def __init__(self, sku: str, nombre: str, descripcion: str,
                 precio_centavos: int, stock: int,
                 identificador: int | None = None,
                 creado_en: datetime | None = None) -> None:
        super().__init__(identificador)
        self.sku = sku
        self.nombre = nombre
        self.descripcion = str(descripcion).strip()
        self.precio_centavos = precio_centavos
        self.stock = stock
        self.creado_en = creado_en

    @property
    def sku(self) -> str:
        return self._sku

    @sku.setter
    def sku(self, valor: str) -> None:
        valor = str(valor).strip().upper()
        if not re.fullmatch(r"[A-Z0-9][A-Z0-9._-]{1,49}", valor):
            raise ErrorDominio(
                "El SKU debe tener entre 2 y 50 caracteres: letras, números, punto, guion o guion bajo."
            )
        self._sku = valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        valor = str(valor).strip()
        if not valor:
            raise ErrorDominio("El nombre del producto es obligatorio.")
        if len(valor) > 150:
            raise ErrorDominio("El nombre del producto admite hasta 150 caracteres.")
        self._nombre = valor

    @property
    def precio_centavos(self) -> int:
        return self._precio_centavos

    @precio_centavos.setter
    def precio_centavos(self, valor: int) -> None:
        if not isinstance(valor, int) or isinstance(valor, bool) or valor <= 0:
            raise ErrorDominio("El precio debe ser un entero positivo en centavos.")
        self._precio_centavos = valor

    @property
    def stock(self) -> int:
        return self._stock

    @stock.setter
    def stock(self, valor: int) -> None:
        if not isinstance(valor, int) or isinstance(valor, bool) or valor < 0:
            raise ErrorDominio("El stock debe ser un entero mayor o igual que cero.")
        self._stock = valor

    def descontar_stock(self, cantidad: int) -> None:
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
            raise ErrorDominio("La cantidad debe ser un entero positivo.")
        if cantidad > self.stock:
            raise ErrorDominio("No existe stock suficiente para el producto.")
        self.stock -= cantidad

    def reponer_stock(self, cantidad: int) -> None:
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
            raise ErrorDominio("La cantidad debe ser un entero positivo.")
        self.stock += cantidad


class DetallePedido(Entidad):
    def __init__(self, producto: Producto, cantidad: int,
                 identificador: int | None = None,
                 precio_unitario_centavos: int | None = None) -> None:
        super().__init__(identificador)
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
            raise ErrorDominio("La cantidad debe ser un entero positivo.")
        self.producto = producto
        self.cantidad = cantidad
        self.precio_unitario_centavos = (
            producto.precio_centavos if precio_unitario_centavos is None
            else precio_unitario_centavos
        )
        if self.precio_unitario_centavos <= 0:
            raise ErrorDominio("El precio unitario debe ser positivo.")

    @property
    def subtotal_centavos(self) -> int:
        return self.cantidad * self.precio_unitario_centavos


class Pedido(Entidad):
    def __init__(self, cliente: Cliente,
                 estado: EstadoPedido | str = EstadoPedido.CREADO,
                 detalles: list[DetallePedido] | None = None,
                 identificador: int | None = None,
                 creado_en: datetime | None = None) -> None:
        super().__init__(identificador)
        self.cliente = cliente
        try:
            self.estado = EstadoPedido(estado)
        except ValueError as error:
            raise ErrorDominio("El estado del pedido no es válido.") from error
        self.detalles = list(detalles or [])
        self.creado_en = creado_en

    @property
    def total_centavos(self) -> int:
        return sum(detalle.subtotal_centavos for detalle in self.detalles)

    def _exigir_creado(self) -> None:
        if self.estado is not EstadoPedido.CREADO:
            raise ErrorDominio("Solo se pueden modificar pedidos en estado CREADO.")

    def agregar_detalle(self, detalle: DetallePedido) -> None:
        self._exigir_creado()
        existente = next(
            (actual for actual in self.detalles
             if actual.producto.id is not None
             and actual.producto.id == detalle.producto.id),
            None,
        )
        if existente is None:
            self.detalles.append(detalle)
        else:
            existente.cantidad += detalle.cantidad

    def quitar_detalle(self, producto_id: int) -> DetallePedido:
        self._exigir_creado()
        for indice, detalle in enumerate(self.detalles):
            if detalle.producto.id == producto_id:
                return self.detalles.pop(indice)
        raise ErrorDominio("El producto no pertenece al pedido.")

    def cambiar_estado(self, nuevo_estado: EstadoPedido | str) -> None:
        try:
            nuevo = EstadoPedido(nuevo_estado)
        except ValueError as error:
            raise ErrorDominio("El estado del pedido no es válido.") from error
        if self.estado is EstadoPedido.CANCELADO:
            raise ErrorDominio("Un pedido cancelado no puede cambiar de estado.")
        if nuevo is EstadoPedido.CONFIRMADO and not self.detalles:
            raise ErrorDominio("No se puede confirmar un pedido sin productos.")
        if nuevo is EstadoPedido.CREADO and self.estado is not EstadoPedido.CREADO:
            raise ErrorDominio("Un pedido finalizado no puede volver a CREADO.")
        self.estado = nuevo
