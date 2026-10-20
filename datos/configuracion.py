"""Configuración de conexión leída desde variables de entorno o `.env`."""

from dataclasses import dataclass
from pathlib import Path

from decouple import config


@dataclass(frozen=True)
class ConfiguracionBaseDatos:
    motor: str
    ruta_sqlite: str
    nombre: str
    servidor: str
    puerto: int
    usuario: str
    contrasena: str

    @classmethod
    def desde_entorno(cls) -> "ConfiguracionBaseDatos":
        return cls(
            motor=config("DB_ENGINE", default="sqlite").strip().lower(),
            ruta_sqlite=config("SQLITE_PATH", default="datos/tienda_online.db"),
            nombre=config("DB_NAME", default="tienda_online"),
            servidor=config("DB_HOST", default="127.0.0.1"),
            puerto=config("DB_PORT", default=3306, cast=int),
            usuario=config("DB_USER", default="tienda_app"),
            contrasena=config("DB_PASSWORD", default=""),
        )

    def ruta_sqlite_absoluta(self) -> Path:
        ruta = Path(self.ruta_sqlite)
        if ruta.is_absolute():
            return ruta
        return Path(__file__).resolve().parents[1] / ruta
