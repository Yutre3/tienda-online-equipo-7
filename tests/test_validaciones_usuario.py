from datetime import date
import importlib

import pytest


def _validaciones():
    return importlib.import_module("auxiliares.validaciones")


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [("6-k", "6-K"), ("12.345.678-5", "12345678-5")],
)
def test_validar_rut_acepta_digito_k_y_normaliza(entrada: str, esperado: str) -> None:
    assert _validaciones().validar_rut(entrada) == esperado


@pytest.mark.parametrize("rut", ["", "12.345.678-9", "12345678", "abc-k"])
def test_validar_rut_rechaza_formato_o_digito_incorrecto(rut: str) -> None:
    with pytest.raises(ValueError, match="RUT"):
        _validaciones().validar_rut(rut)


def test_validar_correo_normaliza_y_rechaza_formato_incorrecto() -> None:
    validar_correo = _validaciones().validar_correo

    assert validar_correo(" ANA.PEREZ@EJEMPLO.CL ") == "ana.perez@ejemplo.cl"
    with pytest.raises(ValueError, match="correo"):
        validar_correo("ana@dominio")


@pytest.mark.parametrize("valor", ["", " ", "x" * 26])
def test_validar_dato_obligatorio_rechaza_vacio_o_mas_de_25_caracteres(valor: str) -> None:
    with pytest.raises(ValueError, match="25|obligatorio"):
        _validaciones().validar_dato_obligatorio(valor)


def test_validar_fecha_y_genero_devuelven_tipos_de_dominio() -> None:
    validaciones = _validaciones()

    assert validaciones.validar_fecha_nacimiento("29/02/2024") == date(2024, 2, 29)
    assert validaciones.validar_genero("3") == 3
    with pytest.raises(ValueError, match="fecha"):
        validaciones.validar_fecha_nacimiento("31/02/2024")
    with pytest.raises(ValueError, match="género"):
        validaciones.validar_genero("4")


def test_validar_contrasenia_exige_largo_mayuscula_minuscula_numero_y_simbolo() -> None:
    validar = _validaciones().validar_contrasenia

    assert validar("Segura1!") == "Segura1!"
    for invalida in ("Corta1!", "minuscula1!", "MAYUSCULA1!", "SinNumero!", "SinSimbolo1"):
        with pytest.raises(ValueError, match="contraseña"):
            validar(invalida)


def test_validar_contrasenia_rechaza_mas_de_15_caracteres() -> None:
    with pytest.raises(ValueError, match="contraseña"):
        _validaciones().validar_contrasenia("MuyLargaSegura123!")
