"""Configuración portable de la conexión a MariaDB."""

from dataclasses import dataclass
import os
from pathlib import Path
import re


RAIZ_PROYECTO = Path(__file__).resolve().parents[1]


def _cargar_env(ruta: Path = RAIZ_PROYECTO / ".env") -> None:
    """Carga pares CLAVE=VALOR sin reemplazar variables del sistema."""
    if not ruta.exists():
        return
    for numero, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        if "=" not in linea:
            raise ValueError(f"Línea {numero} inválida en {ruta.name}.")
        clave, valor = linea.split("=", 1)
        clave = clave.strip()
        valor = valor.strip().strip("\"'")
        if not clave:
            raise ValueError(f"Línea {numero} sin clave en {ruta.name}.")
        os.environ.setdefault(clave, valor)


@dataclass(frozen=True)
class ConfiguracionBD:
    host: str
    puerto: int
    nombre: str
    usuario: str
    contrasena: str

    @classmethod
    def desde_entorno(cls) -> "ConfiguracionBD":
        _cargar_env()
        nombre = os.getenv("DB_NAME", "tienda_online")
        if not re.fullmatch(r"[A-Za-z0-9_]+", nombre):
            raise ValueError("DB_NAME solo puede contener letras, números y guion bajo.")
        puerto = int(os.getenv("DB_PORT", "3306"))
        if not 1 <= puerto <= 65535:
            raise ValueError("DB_PORT debe estar entre 1 y 65535.")
        return cls(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            puerto=puerto,
            nombre=nombre,
            usuario=os.getenv("DB_USER", "root"),
            contrasena=os.getenv("DB_PASSWORD", ""),
        )
