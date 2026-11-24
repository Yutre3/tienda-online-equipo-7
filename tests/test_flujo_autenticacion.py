from datetime import date

import bcrypt
import pytest

import app
from auxiliares import recuperar_acceso
from datos.modelos import PaisModelo, UsuarioModelo
from negocio import ErrorDominio, TiendaServicio
from presentacion.presentacion_usuario import preparar_primer_usuario


def _pais() -> PaisModelo:
    return PaisModelo.create(
        pais="Chile",
        nacionalidad="Chilena",
        iso2="CL",
        iso3="CHL",
        habilitado=True,
    )


def _usuario(
    servicio: TiendaServicio,
    pais: PaisModelo,
    *,
    rut: str = "12.345.678-5",
    correo: str = "ana@ejemplo.cl",
    contrasenia: str = "Segura1!",
):
    return servicio.registrar_usuario(
        rut=rut,
        nombre="Ana",
        apellido="Pérez",
        correo=correo,
        pais_id=pais.id_pais,
        fecha_nacimiento=date(1990, 5, 10),
        genero=2,
        contrasenia=contrasenia,
    )


def test_estado_de_acceso_distingue_los_cuatro_escenarios(base_pruebas) -> None:
    servicio = TiendaServicio()
    assert servicio.estado_acceso_usuarios() == "sin_usuarios"

    pais = _pais()
    usuario = _usuario(servicio, pais)
    assert servicio.estado_acceso_usuarios() == "disponible"

    usuario.password = "hash-invalido"
    usuario.save()
    assert servicio.estado_acceso_usuarios() == "sin_password_valido"

    usuario.habilitado = False
    usuario.save()
    assert servicio.estado_acceso_usuarios() == "sin_habilitados"


@pytest.mark.parametrize(
    ("correo", "clave", "deshabilitar"),
    [
        ("ana@ejemplo.cl", "Incorrecta1!", False),
        ("nadie@ejemplo.cl", "Incorrecta1!", False),
        ("ana@ejemplo.cl", "Segura1!", True),
    ],
)
def test_credenciales_rechazadas_no_abren_el_menu(
    base_pruebas, monkeypatch, correo: str, clave: str, deshabilitar: bool
) -> None:
    servicio = TiendaServicio()
    usuario = _usuario(servicio, _pais())
    if deshabilitar:
        servicio.deshabilitar_usuario(usuario.rut)
        _usuario(
            servicio,
            usuario.pais,
            rut="6-K",
            correo="cuenta.activa@ejemplo.cl",
        )
    entradas = iter([correo, "n"])
    menu_abierto = False

    def menu_prohibido(*args, **kwargs) -> None:
        nonlocal menu_abierto
        menu_abierto = True

    monkeypatch.setattr(app, "menu_principal", menu_prohibido)

    resultado = app.ejecutar_aplicacion(
        servicio,
        entrada=lambda _: next(entradas),
        salida=lambda _: None,
        lector_contrasenia=lambda _: clave,
    )

    assert resultado == 0
    assert menu_abierto is False


def test_login_correcto_abre_menu_y_logout_vuelve_al_login(base_pruebas) -> None:
    servicio = TiendaServicio()
    _usuario(servicio, _pais())
    entradas = iter(["ana@ejemplo.cl", "0", "", "n"])
    mensajes: list[str] = []

    resultado = app.ejecutar_aplicacion(
        servicio,
        entrada=lambda _: next(entradas),
        salida=mensajes.append,
        lector_contrasenia=lambda _: "Segura1!",
    )

    texto = "\n".join(mensajes)
    assert resultado == 0
    assert "Administrar clientes" in texto
    assert "Sesión cerrada" in texto
    assert texto.count("Inicio de sesión cancelado") == 1


def test_cancelar_login_sale_sin_abrir_menu(base_pruebas, monkeypatch) -> None:
    _usuario(TiendaServicio(), _pais())
    entradas = iter(["", "n"])
    menu_abierto = False

    def menu_prohibido(*args, **kwargs) -> None:
        nonlocal menu_abierto
        menu_abierto = True

    monkeypatch.setattr(app, "menu_principal", menu_prohibido)

    resultado = app.ejecutar_aplicacion(
        TiendaServicio(),
        entrada=lambda _: next(entradas),
        salida=lambda _: None,
    )

    assert resultado == 0
    assert menu_abierto is False


def test_alta_inicial_crea_solo_el_primer_usuario_con_hash(base_pruebas) -> None:
    pais = _pais()
    servicio = TiendaServicio()
    entradas = iter(
        [
            "12.345.678-5",
            "Ana",
            "Pérez",
            "ana@ejemplo.cl",
            "Chile",
            str(pais.id_pais),
            "10/05/1990",
            "2",
        ]
    )

    usuario = preparar_primer_usuario(
        servicio,
        entrada=lambda _: next(entradas),
        salida=lambda _: None,
        lector_contrasenia=lambda _: "Segura1!",
    )

    assert UsuarioModelo.select().count() == 1
    assert bcrypt.checkpw(b"Segura1!", usuario.password.encode("ascii"))
    with pytest.raises(ErrorDominio, match="instalación inicial"):
        preparar_primer_usuario(
            servicio,
            entrada=lambda _: pytest.fail("No debe solicitar otro usuario"),
            salida=lambda _: None,
            lector_contrasenia=lambda _: "OtraSegura1!",
        )


def test_alta_inicial_sin_pais_termina_con_error_explicado(base_pruebas) -> None:
    with pytest.raises(ErrorDominio, match="país habilitado"):
        preparar_primer_usuario(
            TiendaServicio(),
            entrada=lambda _: pytest.fail("No debe abrir un formulario imposible"),
            salida=lambda _: None,
            lector_contrasenia=lambda _: "Segura1!",
        )


def test_hash_invalido_bloquea_y_orienta_sin_crear_otra_cuenta(
    base_pruebas, monkeypatch
) -> None:
    usuario = _usuario(TiendaServicio(), _pais())
    usuario.password = "invalido"
    usuario.save()
    mensajes: list[str] = []
    monkeypatch.setattr(
        app,
        "menu_principal",
        lambda *args, **kwargs: pytest.fail("No debe abrir el menú"),
    )

    resultado = app.ejecutar_aplicacion(
        TiendaServicio(), entrada=lambda _: "", salida=mensajes.append
    )

    assert resultado == 2
    assert UsuarioModelo.select().count() == 1
    assert "python -m auxiliares.recuperar_acceso" in "\n".join(mensajes)


def test_cuentas_deshabilitadas_no_se_reactivan_automaticamente(
    base_pruebas,
) -> None:
    servicio = TiendaServicio()
    usuario = _usuario(servicio, _pais())
    servicio.deshabilitar_usuario(usuario.rut)
    mensajes: list[str] = []

    resultado = app.ejecutar_aplicacion(
        servicio, entrada=lambda _: "", salida=mensajes.append
    )

    usuario = UsuarioModelo.get_by_id(usuario.id_usuario)
    assert resultado == 2
    assert usuario.habilitado is False
    assert "no habilita" in "\n".join(mensajes).lower()


def test_logout_reevalua_si_la_ultima_cuenta_fue_deshabilitada(
    base_pruebas, monkeypatch
) -> None:
    servicio = TiendaServicio()
    usuario = _usuario(servicio, _pais())
    mensajes: list[str] = []

    def deshabilitar_y_cerrar(*args, **kwargs) -> None:
        servicio.deshabilitar_usuario(usuario.rut)

    monkeypatch.setattr(app, "menu_principal", deshabilitar_y_cerrar)

    resultado = app.ejecutar_aplicacion(
        servicio,
        entrada=lambda _: usuario.correo,
        salida=mensajes.append,
        lector_contrasenia=lambda _: "Segura1!",
    )

    assert resultado == 2
    assert servicio.estado_acceso_usuarios() == "sin_habilitados"


def test_recuperacion_cambia_solo_hash_y_conserva_estado(base_pruebas) -> None:
    servicio = TiendaServicio()
    usuario = _usuario(servicio, _pais())
    servicio.deshabilitar_usuario(usuario.rut)
    antes = (
        usuario.rut,
        usuario.nombre,
        usuario.apellido,
        usuario.correo,
        usuario.pais_id,
        usuario.fecha_nacimiento,
        usuario.genero,
    )

    recuperado = servicio.cambiar_contrasenia_usuario_existente(
        usuario.correo, "NuevaSegura1!"
    )

    despues = (
        recuperado.rut,
        recuperado.nombre,
        recuperado.apellido,
        recuperado.correo,
        recuperado.pais_id,
        recuperado.fecha_nacimiento,
        recuperado.genero,
    )
    assert despues == antes
    assert recuperado.habilitado is False
    assert bcrypt.checkpw(b"NuevaSegura1!", recuperado.password.encode("ascii"))


def test_comando_local_recupera_una_cuenta_existente(base_pruebas) -> None:
    servicio = TiendaServicio()
    usuario = _usuario(servicio, _pais())
    mensajes: list[str] = []

    resultado = recuperar_acceso.main(
        servicio=servicio,
        entrada=lambda _: usuario.correo,
        salida=mensajes.append,
        lector_contrasenia=lambda _: "NuevaSegura1!",
    )

    assert resultado == 0
    assert servicio.autenticar_usuario(usuario.correo, "NuevaSegura1!")
    assert "actualizada" in "\n".join(mensajes).lower()
