"""Lectura segura de valores desde la consola."""

from collections.abc import Callable


Entrada = Callable[[str], str]
Salida = Callable[[str], None]


def solicitar_texto(
    mensaje: str,
    *,
    entrada: Entrada = input,
    salida: Salida = print,
) -> str:
    while True:
        valor = entrada(mensaje).strip()
        if valor:
            return valor
        salida("El valor no puede estar vacío.")


def solicitar_entero(
    mensaje: str,
    *,
    minimo: int | None = None,
    entrada: Entrada = input,
    salida: Salida = print,
) -> int:
    while True:
        try:
            valor = int(entrada(mensaje).strip())
        except ValueError:
            salida("Ingrese un número entero válido.")
            continue
        if minimo is not None and valor < minimo:
            salida(f"El valor debe ser mayor o igual que {minimo}.")
            continue
        return valor
