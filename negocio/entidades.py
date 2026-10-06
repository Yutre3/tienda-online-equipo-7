from __future__ import annotations

from abc import ABC
import re


class Entidad(ABC):
    """Clase base reutilizable para las entidades persistentes."""

    def __init__(self, identificador: int | None = None) -> None:
        if identificador is not None and identificador <= 0:
            raise ValueError("El identificador debe ser un entero positivo.")
        self._id = identificador

    @property
    def id(self) -> int | None:
        return self._id

    def _asignar_id(self, identificador: int) -> None:
        if identificador <= 0:
            raise ValueError("El identificador debe ser un entero positivo.")
        if self._id is not None:
            raise ValueError("La entidad ya tiene un identificador asignado.")
        self._id = identificador


class Cliente(Entidad):
    def __init__(self, nombre: str, correo: str,
                 identificador: int | None = None) -> None:
        super().__init__(identificador)
        self.nombre = nombre
        self.correo = correo

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        valor = valor.strip()
        if not valor:
            raise ValueError("El nombre del cliente es obligatorio.")
        self._nombre = valor

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        valor = valor.strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", valor):
            raise ValueError("El correo del cliente no es válido.")
        self._correo = valor


class Producto(Entidad):
    def __init__(self, nombre: str, descripcion: str, precio_centavos: int,
                 stock: int, identificador: int | None = None) -> None:
        super().__init__(identificador)
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio_centavos = precio_centavos
        self.stock = stock

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        valor = valor.strip()
        if not valor:
            raise ValueError("El nombre del producto es obligatorio.")
        self._nombre = valor

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        self._descripcion = valor.strip()

    @property
    def precio_centavos(self) -> int:
        return self._precio_centavos

    @precio_centavos.setter
    def precio_centavos(self, valor: int) -> None:
        if not isinstance(valor, int) or isinstance(valor, bool) or valor <= 0:
            raise ValueError("El precio debe ser un entero positivo en centavos.")
        self._precio_centavos = valor

    @property
    def stock(self) -> int:
        return self._stock

    @stock.setter
    def stock(self, valor: int) -> None:
        if not isinstance(valor, int) or isinstance(valor, bool) or valor < 0:
            raise ValueError("El stock debe ser un entero mayor o igual que cero.")
        self._stock = valor

    def descontar_stock(self, cantidad: int) -> None:
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
            raise ValueError("La cantidad debe ser un entero positivo.")
        if cantidad > self._stock:
            raise ValueError("No existe stock suficiente para el producto.")
        self._stock -= cantidad


class DetallePedido(Entidad):
    def __init__(self, producto: Producto, cantidad: int,
                 precio_unitario_centavos: int | None = None,
                 identificador: int | None = None) -> None:
        super().__init__(identificador)
        if not isinstance(producto, Producto):
            raise TypeError("El detalle debe contener un producto válido.")
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
            raise ValueError("La cantidad debe ser un entero positivo.")
        precio = producto.precio_centavos if precio_unitario_centavos is None else precio_unitario_centavos
        if not isinstance(precio, int) or isinstance(precio, bool) or precio <= 0:
            raise ValueError("El precio unitario debe ser un entero positivo.")
        self._producto = producto
        self._cantidad = cantidad
        self._precio_unitario_centavos = precio

    @property
    def producto(self) -> Producto:
        return self._producto

    @property
    def cantidad(self) -> int:
        return self._cantidad

    @property
    def precio_unitario_centavos(self) -> int:
        return self._precio_unitario_centavos

    @property
    def subtotal_centavos(self) -> int:
        return self._cantidad * self._precio_unitario_centavos


class Pedido(Entidad):
    ESTADOS_VALIDOS = {"CREADO", "CONFIRMADO", "CANCELADO"}

    def __init__(self, cliente: Cliente, estado: str = "CREADO",
                 total_centavos: int = 0,
                 identificador: int | None = None) -> None:
        super().__init__(identificador)
        if not isinstance(cliente, Cliente):
            raise TypeError("El pedido debe pertenecer a un cliente válido.")
        if estado not in self.ESTADOS_VALIDOS:
            raise ValueError("El estado del pedido no es válido.")
        if not isinstance(total_centavos, int) or total_centavos < 0:
            raise ValueError("El total del pedido debe ser un entero no negativo.")
        self._cliente = cliente
        self._estado = estado
        self._total_centavos = total_centavos
        self._detalles: list[DetallePedido] = []

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def total_centavos(self) -> int:
        return self._total_centavos

    @property
    def detalles(self) -> tuple[DetallePedido, ...]:
        return tuple(self._detalles)

    def agregar_detalle(self, detalle: DetallePedido) -> None:
        if self._estado != "CREADO":
            raise ValueError("Solo se pueden modificar pedidos en estado CREADO.")
        if any(item.producto.id == detalle.producto.id for item in self._detalles):
            raise ValueError("El producto ya está incluido en el pedido.")
        self._detalles.append(detalle)
        self._total_centavos += detalle.subtotal_centavos
