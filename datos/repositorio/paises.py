"""Funciones Peewee para consultar países habilitados."""

from datos.modelos import PaisModelo
from negocio.entidades import ErrorDominio


def listado_paises() -> list[PaisModelo]:
    return list(
        PaisModelo.select()
        .where(PaisModelo.habilitado == True)  # noqa: E712
        .order_by(PaisModelo.pais)
    )


def buscar_paises(nombre_pais: str) -> list[PaisModelo]:
    return list(
        PaisModelo.select()
        .where(
            (PaisModelo.pais.contains(nombre_pais.strip()))
            & (PaisModelo.habilitado == True)  # noqa: E712
        )
        .order_by(PaisModelo.pais)
    )


def obtener_pais_id(identificador: int) -> PaisModelo:
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
