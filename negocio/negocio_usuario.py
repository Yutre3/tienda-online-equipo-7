"""Reglas de seguridad y normalización del módulo de usuarios."""

import bcrypt

from auxiliares.validaciones import validar_contrasenia


def crear_hash_contrasenia(contrasenia: str) -> str:
    """Devuelve un hash bcrypt apto para un CharField de 60 caracteres."""
    segura = validar_contrasenia(contrasenia)
    return bcrypt.hashpw(segura.encode("utf-8"), bcrypt.gensalt()).decode("ascii")
