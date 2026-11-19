"""Validaciones reutilizables para el módulo de usuarios."""

from datetime import date, datetime
import re


SIMBOLOS_CONTRASENIA = "!@#$%&/"


def validar_rut(rut: str) -> str:
    """Valida módulo 11 y devuelve el RUT con verificador en mayúscula."""
    valor = str(rut).strip()
    if not re.fullmatch(r"\d{1,3}(?:\.?\d{3})*-[0-9kK]", valor):
        raise ValueError("El formato del RUT no es válido.")

    cuerpo, verificador = valor.replace(".", "").split("-")
    suma = sum(
        int(digito) * (2 + indice % 6)
        for indice, digito in enumerate(reversed(cuerpo))
    )
    resultado = 11 - suma % 11
    esperado = "0" if resultado == 11 else "K" if resultado == 10 else str(resultado)
    if verificador.upper() != esperado:
        raise ValueError("El dígito verificador del RUT no es válido.")
    return f"{cuerpo}-{verificador.upper()}"


def validar_dato_obligatorio(valor: str, maximo: int = 25) -> str:
    resultado = str(valor).strip()
    if not resultado:
        raise ValueError("El dato es obligatorio.")
    if len(resultado) > maximo:
        raise ValueError(f"El dato admite como máximo {maximo} caracteres.")
    return resultado


def validar_dato_opcional(valor: str, maximo: int = 25) -> str:
    resultado = str(valor).strip()
    if not resultado:
        return ""
    if len(resultado) > maximo:
        raise ValueError(f"El dato admite como máximo {maximo} caracteres.")
    return resultado


def validar_correo(correo: str) -> str:
    resultado = str(correo).strip().lower()
    if len(resultado) > 191 or not re.fullmatch(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", resultado
    ):
        raise ValueError("El correo no tiene un formato válido.")
    return resultado


def validar_fecha_nacimiento(valor: str) -> date:
    try:
        return datetime.strptime(str(valor).strip(), "%d/%m/%Y").date()
    except ValueError as error:
        raise ValueError("La fecha debe ser válida y usar el formato dd/mm/aaaa.") from error


def validar_genero(valor: str | int) -> int:
    try:
        genero = int(valor)
    except (TypeError, ValueError) as error:
        raise ValueError("El género debe ser una opción entre 1 y 3.") from error
    if genero not in (1, 2, 3):
        raise ValueError("El género debe ser una opción entre 1 y 3.")
    return genero


def validar_contrasenia(contrasenia: str) -> str:
    valor = str(contrasenia)
    condiciones = (
        8 <= len(valor) <= 15,
        any(caracter.isupper() for caracter in valor),
        any(caracter.islower() for caracter in valor),
        any(caracter.isdigit() for caracter in valor),
        any(caracter in SIMBOLOS_CONTRASENIA for caracter in valor),
    )
    if not all(condiciones):
        raise ValueError(
            "La contraseña debe tener de 8 a 15 caracteres e incluir mayúscula, "
            "minúscula, número y un símbolo permitido (!@#$%&/)."
        )
    return valor
