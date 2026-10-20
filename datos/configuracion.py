"""Configuración de conexión leída desde variables de entorno o `.env`."""

from dataclasses import dataclass

from decouple import config


@dataclass(frozen=True)
class ConfiguracionBaseDatos:
    nombre: str
    servidor: str
    puerto: int
    usuario: str
    contrasena: str

    @classmethod
    def desde_entorno(cls) -> "ConfiguracionBaseDatos":
        return cls(
            nombre=config("DB_NAME", default="tienda_online"),
            servidor=config("DB_HOST", default="127.0.0.1"),
            puerto=config("DB_PORT", default=3306, cast=int),
            usuario=config("DB_USER", default="tienda_app"),
            contrasena=config("DB_PASSWORD", default=""),
        )
