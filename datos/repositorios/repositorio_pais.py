"""Consultas Peewee de países disponibles para usuarios."""

from datos.modelos import PaisModelo
from negocio.entidades import ErrorDominio


class RepositorioPaises:
    def listar_habilitados(self) -> list[PaisModelo]:
        return list(
            PaisModelo.select()
            .where(PaisModelo.habilitado == True)  # noqa: E712
            .order_by(PaisModelo.pais)
        )

    def buscar(self, nombre: str) -> list[PaisModelo]:
        return list(
            PaisModelo.select()
            .where(
                (PaisModelo.pais.contains(nombre.strip()))
                & (PaisModelo.habilitado == True)  # noqa: E712
            )
            .order_by(PaisModelo.pais)
        )

    def obtener(self, identificador: int) -> PaisModelo:
        pais = (
            PaisModelo.select()
            .where(
                (PaisModelo.id_pais == identificador)
                & (PaisModelo.habilitado == True)  # noqa: E712
            )
            .first()
        )
        if pais is None:
            raise ErrorDominio("No existe un país habilitado con ese ID.")
        return pais


def listado_paises() -> list[PaisModelo]:
    return RepositorioPaises().listar_habilitados()


def buscar_paises(nombre_pais: str) -> list[PaisModelo]:
    return RepositorioPaises().buscar(nombre_pais)


def obtener_pais_id(identificador: int) -> PaisModelo:
    return RepositorioPaises().obtener(identificador)
