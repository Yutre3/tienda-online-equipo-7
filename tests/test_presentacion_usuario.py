from datetime import date
import importlib

import bcrypt

from auxiliares.info_app import NOMBRE_APLICACION
from datos.modelos import PaisModelo
from negocio import TiendaServicio
from presentacion.menu import menu_principal


def _presentacion():
    return importlib.import_module("presentacion.presentacion_usuario")


def _pais() -> PaisModelo:
    return PaisModelo.create(
        pais="Chile",
        nacionalidad="Chilena",
        iso2="CL",
        iso3="CHL",
        habilitado=True,
    )


def _usuario(servicio: TiendaServicio, pais: PaisModelo):
    return servicio.registrar_usuario(
        rut="12.345.678-5",
        nombre="Ana",
        apellido="Pérez",
        correo="ana@ejemplo.cl",
        pais_id=pais.id_pais,
        fecha_nacimiento=date(1990, 5, 10),
        genero=2,
        contrasenia="Segura1!",
    )


def test_solicitar_rut_reintenta_solo_el_campo_incorrecto() -> None:
    entradas = iter(["12.345.678-9", "6-k"])
    mensajes: list[str] = []

    rut = _presentacion().solicitar_rut(
        "RUT: ", entrada=lambda _: next(entradas), salida=mensajes.append
    )

    assert rut == "6-K"
    assert any("verificador" in mensaje for mensaje in mensajes)


def test_solicitar_pais_muestra_coincidencias_y_exige_id_mostrado(base_pruebas) -> None:
    pais = _pais()
    entradas = iter(["chi", "99", str(pais.id_pais)])
    mensajes: list[str] = []

    resultado = _presentacion().solicitar_pais(
        TiendaServicio(),
        entrada=lambda _: next(entradas),
        salida=mensajes.append,
    )

    assert resultado == pais.id_pais
    assert any("Chile" in mensaje for mensaje in mensajes)
    assert any("ID" in mensaje and "mostrados" in mensaje for mensaje in mensajes)


def test_solicitar_contrasenia_reintenta_y_no_imprime_la_clave() -> None:
    claves = iter(["debil", "Segura1!"])
    mensajes: list[str] = []

    resultado = _presentacion().solicitar_contrasenia(
        "Contraseña: ",
        lector_contrasenia=lambda _: next(claves),
        salida=mensajes.append,
    )

    assert resultado == "Segura1!"
    assert "Segura1!" not in "\n".join(mensajes)
    assert any("contraseña" in mensaje.lower() for mensaje in mensajes)


def test_crear_usuario_registra_y_muestra_exito_solo_despues_de_guardar(base_pruebas) -> None:
    pais = _pais()
    servicio = TiendaServicio()
    entradas = iter(
        [
            "12.345.678-5",
            "Ana",
            "Pérez",
            "ANA@EJEMPLO.CL",
            "chi",
            str(pais.id_pais),
            "10/05/1990",
            "2",
        ]
    )
    mensajes: list[str] = []

    creado = _presentacion().crear_usuario(
        servicio,
        entrada=lambda _: next(entradas),
        salida=mensajes.append,
        lector_contrasenia=lambda _: "Segura1!",
    )

    assert creado.correo == "ana@ejemplo.cl"
    assert bcrypt.checkpw(b"Segura1!", creado.password.encode("ascii"))
    assert mensajes[-1] == "Usuario registrado con ID 1."


def test_modificar_usuario_con_enter_conserva_campos_anteriores(base_pruebas) -> None:
    pais = _pais()
    servicio = TiendaServicio()
    original = _usuario(servicio, pais)
    entradas = iter(
        [original.rut, "", "Ana María", "", "", "", "", ""]
    )
    mensajes: list[str] = []

    actualizado = _presentacion().modificar_usuario(
        servicio,
        entrada=lambda _: next(entradas),
        salida=mensajes.append,
    )

    assert actualizado.nombre == "Ana María"
    assert actualizado.apellido == "Pérez"
    assert actualizado.correo == "ana@ejemplo.cl"
    assert actualizado.pais.id_pais == pais.id_pais
    assert mensajes[-1] == "Usuario actualizado."


def test_eliminar_usuario_pide_confirmacion_y_hace_baja_logica(base_pruebas) -> None:
    pais = _pais()
    servicio = TiendaServicio()
    original = _usuario(servicio, pais)
    entradas = iter([original.rut, "s"])
    mensajes: list[str] = []

    resultado = _presentacion().eliminar_usuario(
        servicio,
        entrada=lambda _: next(entradas),
        salida=mensajes.append,
    )

    assert resultado.habilitado is False
    assert servicio.listar_usuarios(None)[0].id_usuario == original.id_usuario
    assert any("Ana" in mensaje and original.rut in mensaje for mensaje in mensajes)
    assert mensajes[-1] == "Usuario deshabilitado."


def test_tabla_usuarios_muestra_pais_genero_y_estado(base_pruebas) -> None:
    pais = _pais()
    servicio = TiendaServicio()
    usuario = _usuario(servicio, pais)
    usuario = servicio.deshabilitar_usuario(usuario.rut)

    tabla = _presentacion().tabla_usuarios([usuario])

    assert "Chile" in tabla
    assert "Femenino" in tabla
    assert "Deshabilitado" in tabla


def test_busquedas_por_rut_y_correo_muestran_el_usuario_normalizado(
    base_pruebas,
) -> None:
    pais = _pais()
    servicio = TiendaServicio()
    usuario = _usuario(servicio, pais)
    mensajes: list[str] = []

    por_rut = _presentacion().mostrar_usuario_por_rut(
        servicio,
        entrada=lambda _: "12.345.678-5",
        salida=mensajes.append,
    )
    por_correo = _presentacion().mostrar_usuario_por_correo(
        servicio,
        entrada=lambda _: " ANA@EJEMPLO.CL ",
        salida=mensajes.append,
    )

    assert por_rut.id_usuario == usuario.id_usuario
    assert por_correo.id_usuario == usuario.id_usuario
    assert sum(usuario.rut in mensaje for mensaje in mensajes) == 2
    assert sum(usuario.correo in mensaje for mensaje in mensajes) == 2


def test_login_usuario_permite_cancelar_sin_solicitar_contrasenia(
    base_pruebas,
) -> None:
    mensajes: list[str] = []
    contrasenia_solicitada = False

    def leer_contrasenia(_: str) -> str:
        nonlocal contrasenia_solicitada
        contrasenia_solicitada = True
        return "no-debe-usarse"

    resultado = _presentacion().login_usuario(
        TiendaServicio(),
        entrada=lambda _: "",
        salida=mensajes.append,
        lector_contrasenia=leer_contrasenia,
    )

    assert resultado is None
    assert contrasenia_solicitada is False
    assert mensajes[-1] == "Inicio de sesión cancelado."


def test_login_usuario_permite_cancelar_en_la_contrasenia(base_pruebas) -> None:
    mensajes: list[str] = []

    resultado = _presentacion().login_usuario(
        TiendaServicio(),
        entrada=lambda _: "ana@ejemplo.cl",
        salida=mensajes.append,
        lector_contrasenia=lambda _: "",
    )

    assert resultado is None
    assert mensajes[-1] == "Inicio de sesión cancelado."


def test_menu_principal_integra_submenu_usuarios_sin_alterar_salida(base_pruebas) -> None:
    entradas = iter(["5", "0", "0"])
    salidas: list[str] = []

    menu_principal(
        TiendaServicio(),
        entrada=lambda _: next(entradas),
        salida=salidas.append,
    )

    assert any("Administrar usuarios" in salida for salida in salidas)
    assert any("USUARIOS" in salida for salida in salidas)
    assert salidas[-1] == "Programa finalizado."


def test_menu_principal_abre_acceso_y_continua_tras_login_correcto(
    base_pruebas,
) -> None:
    pais = _pais()
    usuario = _usuario(TiendaServicio(), pais)
    entradas = iter(["6", " ANA@EJEMPLO.CL ", "0"])
    salidas: list[str] = []

    menu_principal(
        TiendaServicio(),
        entrada=lambda _: next(entradas),
        salida=salidas.append,
        lector_contrasenia=lambda _: "Segura1!",
    )

    texto = "\n".join(salidas)
    assert "Iniciar sesión" in texto
    assert f"Bienvenida, {usuario.nombre}." in salidas
    posicion_bienvenida = salidas.index(f"Bienvenida, {usuario.nombre}.")
    assert any(
        NOMBRE_APLICACION in mensaje
        for mensaje in salidas[posicion_bienvenida + 1 :]
    )
    assert salidas[-1] == "Programa finalizado."


def test_submenu_usuarios_ofrece_busquedas_por_rut_y_correo(base_pruebas) -> None:
    pais = _pais()
    usuario = _usuario(TiendaServicio(), pais)
    entradas = iter(
        ["5", "5", usuario.rut, "6", usuario.correo, "0", "0"]
    )
    salidas: list[str] = []

    menu_principal(
        TiendaServicio(),
        entrada=lambda _: next(entradas),
        salida=salidas.append,
    )

    texto = "\n".join(salidas)
    assert "Buscar por RUT" in texto
    assert "Buscar por correo" in texto
    assert texto.count(usuario.rut) == 2
    assert texto.count(usuario.correo) == 2
    assert salidas[-1] == "Programa finalizado."
