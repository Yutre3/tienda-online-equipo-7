"""Compatibilidad con el repositorio funcional de países."""

from datos.modelos import PaisModelo
from datos.repositorio.paises import (
    buscar_paises,
    listado_paises,
    obtener_pais_id,
)


class RepositorioPaises:
    def listar_habilitados(self) -> list[PaisModelo]:
        return listado_paises()

    def buscar(self, nombre: str) -> list[PaisModelo]:
        return buscar_paises(nombre)

    def obtener(self, identificador: int) -> PaisModelo:
        return obtener_pais_id(identificador)


__all__ = [
    "RepositorioPaises",
    "buscar_paises",
    "listado_paises",
    "obtener_pais_id",
]
