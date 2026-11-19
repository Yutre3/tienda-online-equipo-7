from datetime import date
import importlib

import bcrypt
import pytest
from peewee import SqliteDatabase

from datos.conexion import configurar_base_datos, crear_tablas, tablas
from negocio import ErrorDominio, TiendaServicio


def _modelos():
    return importlib.import_module("datos.modelos")


def _crear_pais(nombre: str = "Chile", iso2: str = "CL", iso3: str = "CHL"):
    return _modelos().PaisModelo.create(
        pais=nombre,
        nacionalidad="Chilena",
        iso2=iso2,
        iso3=iso3,
        habilitado=True,
    )


def _registrar_usuario(servicio: TiendaServicio, pais_id: int, **cambios):
    datos = {
        "rut": "12.345.678-5",
        "nombre": "Ana",
        "apellido": "Pérez",
        "correo": "ana@ejemplo.cl",
        "pais_id": pais_id,
        "fecha_nacimiento": date(1990, 5, 10),
        "genero": 2,
        "contrasenia": "Segura1!",
    }
    datos.update(cambios)
    return servicio.registrar_usuario(**datos)


def test_modelos_usuario_y_pais_comparten_base_y_clave_foranea(base_pruebas) -> None:
    modelos = _modelos()

    assert modelos.PaisModelo._meta.table_name == "paises"
    assert modelos.UsuarioModelo._meta.table_name == "usuarios"
    assert modelos.UsuarioModelo.pais.rel_model is modelos.PaisModelo
    assert modelos.UsuarioModelo.pais.column_name == "pais"
    assert modelos.UsuarioModelo.password.max_length == 60
    assert {"paises", "usuarios"} <= set(base_pruebas.get_tables())


def test_modelo_usuario_lee_tabla_preexistente_del_profesor() -> None:
    base = SqliteDatabase(":memory:", pragmas={"foreign_keys": 1})
    configurar_base_datos(base)
    base.connect()
    base.execute_sql(
        """
        CREATE TABLE paises (
            id_pais INTEGER PRIMARY KEY,
            pais VARCHAR(50) NOT NULL,
            nacionalidad VARCHAR(50),
            iso2 VARCHAR(2) NOT NULL,
            iso3 VARCHAR(3) NOT NULL,
            habilitado INTEGER NOT NULL DEFAULT 1
        )
        """
    )
    base.execute_sql(
        """
        CREATE TABLE usuarios (
            id_usuario INTEGER PRIMARY KEY,
            rut VARCHAR(12) NOT NULL UNIQUE,
            nombre VARCHAR(25) NOT NULL,
            apellido VARCHAR(25) NOT NULL,
            correo VARCHAR(191) NOT NULL,
            pais INTEGER NOT NULL REFERENCES paises(id_pais),
            fecha_nacimiento DATE NOT NULL,
            genero INTEGER NOT NULL,
            fecha_incorporacion DATE NOT NULL,
            habilitado INTEGER NOT NULL DEFAULT 1,
            password VARCHAR(60) NOT NULL
        )
        """
    )
    base.execute_sql(
        "INSERT INTO paises VALUES (1, 'Chile', 'Chilena', 'CL', 'CHL', 1)"
    )
    base.execute_sql(
        """
        INSERT INTO usuarios VALUES (
            1, '12345678-5', 'Ana', 'Pérez', 'ana@ejemplo.cl', 1,
            '1990-05-10', 2, '2026-11-18', 1,
            '$2b$12$123456789012345678901u12345678901234567890123456789012'
        )
        """
    )

    usuario = _modelos().UsuarioModelo.select().first()

    assert usuario.pais.pais == "Chile"
    with pytest.raises(ErrorDominio, match="correo"):
        _registrar_usuario(
            TiendaServicio(),
            1,
            rut="6-K",
            correo="ANA@EJEMPLO.CL",
        )
    base.close()


def test_registrar_usuario_guarda_hash_bcrypt_textual_y_no_clave_original(base_pruebas) -> None:
    pais = _crear_pais()

    usuario = _registrar_usuario(TiendaServicio(), pais.id_pais)

    assert usuario.id_usuario == 1
    assert isinstance(usuario.password, str)
    assert len(usuario.password) == 60
    assert usuario.password != "Segura1!"
    assert bcrypt.checkpw(b"Segura1!", usuario.password.encode("ascii"))
    assert usuario.pais.id_pais == pais.id_pais
    assert usuario.habilitado is True


@pytest.mark.parametrize("campo", ["rut", "correo"])
def test_registrar_usuario_impide_rut_o_correo_duplicado(base_pruebas, campo: str) -> None:
    pais = _crear_pais()
    servicio = TiendaServicio()
    _registrar_usuario(servicio, pais.id_pais)
    cambios = {
        "rut": "6-K",
        "correo": "otra@ejemplo.cl",
        campo: "12.345.678-5" if campo == "rut" else "ANA@EJEMPLO.CL",
    }

    with pytest.raises(ErrorDominio, match="RUT|correo"):
        _registrar_usuario(servicio, pais.id_pais, **cambios)


def test_registrar_usuario_impide_mismo_rut_con_distinto_formato(base_pruebas) -> None:
    pais = _crear_pais()
    servicio = TiendaServicio()
    _registrar_usuario(servicio, pais.id_pais)

    with pytest.raises(ErrorDominio, match="RUT"):
        _registrar_usuario(
            servicio,
            pais.id_pais,
            rut="12345678-5",
            correo="otra@ejemplo.cl",
        )


def test_buscar_usuario_por_rut_y_correo_normalizados(base_pruebas) -> None:
    pais = _crear_pais()
    servicio = TiendaServicio()
    creado = _registrar_usuario(servicio, pais.id_pais)

    assert servicio.buscar_usuario_rut("12.345.678-5").id_usuario == creado.id_usuario
    assert servicio.buscar_usuario_correo(" ANA@EJEMPLO.CL ").id_usuario == creado.id_usuario
    with pytest.raises(ErrorDominio, match="usuario"):
        servicio.buscar_usuario_rut("6-K")
    with pytest.raises(ErrorDominio, match="usuario"):
        servicio.buscar_usuario_correo("nadie@ejemplo.cl")


def test_listados_separan_habilitados_deshabilitados_y_general(base_pruebas) -> None:
    pais = _crear_pais()
    servicio = TiendaServicio()
    activo = _registrar_usuario(servicio, pais.id_pais)
    inactivo = _registrar_usuario(
        servicio,
        pais.id_pais,
        rut="6-K",
        correo="inactivo@ejemplo.cl",
    )
    servicio.deshabilitar_usuario(inactivo.rut)

    assert [usuario.id_usuario for usuario in servicio.listar_usuarios(True)] == [activo.id_usuario]
    assert [usuario.id_usuario for usuario in servicio.listar_usuarios(False)] == [inactivo.id_usuario]
    assert [usuario.id_usuario for usuario in servicio.listar_usuarios(None)] == [
        activo.id_usuario,
        inactivo.id_usuario,
    ]


def test_actualizar_usuario_conserva_campos_omitidos_y_no_cambia_password(base_pruebas) -> None:
    chile = _crear_pais()
    peru = _crear_pais("Perú", "PE", "PER")
    servicio = TiendaServicio()
    original = _registrar_usuario(servicio, chile.id_pais)
    hash_original = original.password

    actualizado = servicio.actualizar_usuario(
        original.rut,
        nombre="Ana María",
        pais_id=peru.id_pais,
    )

    assert actualizado.nombre == "Ana María"
    assert actualizado.apellido == "Pérez"
    assert actualizado.correo == "ana@ejemplo.cl"
    assert actualizado.fecha_nacimiento == date(1990, 5, 10)
    assert actualizado.genero == 2
    assert actualizado.pais.id_pais == peru.id_pais
    assert actualizado.password == hash_original


def test_deshabilitar_usuario_conserva_registro_fisico(base_pruebas) -> None:
    pais = _crear_pais()
    servicio = TiendaServicio()
    usuario = _registrar_usuario(servicio, pais.id_pais)

    deshabilitado = servicio.deshabilitar_usuario(usuario.rut)

    assert deshabilitado.habilitado is False
    assert _modelos().UsuarioModelo.select().count() == 1
    assert servicio.buscar_usuario_rut(usuario.rut).id_usuario == usuario.id_usuario


def test_migracion_agrega_password_sin_eliminar_usuarios_antiguos() -> None:
    base = SqliteDatabase(":memory:", pragmas={"foreign_keys": 1})
    configurar_base_datos(base)
    base.connect()
    base.execute_sql(
        """
        CREATE TABLE paises (
            id_pais INTEGER PRIMARY KEY,
            pais VARCHAR(50) NOT NULL,
            nacionalidad VARCHAR(50),
            iso2 VARCHAR(2) NOT NULL,
            iso3 VARCHAR(3) NOT NULL,
            habilitado INTEGER NOT NULL DEFAULT 1
        )
        """
    )
    base.execute_sql(
        """
        CREATE TABLE usuarios (
            id_usuario INTEGER PRIMARY KEY,
            rut VARCHAR(12) NOT NULL UNIQUE,
            nombre VARCHAR(25) NOT NULL,
            apellido VARCHAR(25) NOT NULL,
            correo VARCHAR(191) NOT NULL,
            pais INTEGER NOT NULL REFERENCES paises(id_pais),
            fecha_nacimiento DATE NOT NULL,
            genero INTEGER NOT NULL,
            fecha_incorporacion DATE NOT NULL,
            habilitado INTEGER NOT NULL DEFAULT 1
        )
        """
    )
    base.execute_sql(
        "INSERT INTO paises VALUES (1, 'Chile', 'Chilena', 'CL', 'CHL', 1)"
    )
    base.execute_sql(
        """
        INSERT INTO usuarios VALUES (
            7, '12345678-5', 'Ana', 'Pérez', 'ana@ejemplo.cl', 1,
            '1990-05-10', 2, '2026-10-20', 1
        )
        """
    )

    try:
        crear_tablas()

        columnas = {columna.name for columna in base.get_columns("usuarios")}
        usuario = _modelos().UsuarioModelo.get_by_id(7)
        assert "password" in columnas
        assert usuario.rut == "12345678-5"
        assert usuario.correo == "ana@ejemplo.cl"
        assert usuario.pais.pais == "Chile"
        assert usuario.password is None
        assert _modelos().UsuarioModelo.select().count() == 1
    finally:
        base.close()


def test_usuario_persiste_despues_de_cerrar_y_reabrir_sqlite(tmp_path) -> None:
    ruta = tmp_path / "usuarios.db"
    primera = SqliteDatabase(ruta, pragmas={"foreign_keys": 1})
    configurar_base_datos(primera)
    primera.connect()
    crear_tablas()
    pais = _crear_pais()
    creado = _registrar_usuario(TiendaServicio(), pais.id_pais)
    primera.close()

    segunda = SqliteDatabase(ruta, pragmas={"foreign_keys": 1})
    configurar_base_datos(segunda)
    segunda.connect()
    crear_tablas()
    recuperado = TiendaServicio().buscar_usuario_rut(creado.rut)

    assert recuperado.correo == "ana@ejemplo.cl"
    assert bcrypt.checkpw(b"Segura1!", recuperado.password.encode("ascii"))
    segunda.drop_tables(list(reversed(tablas())))
    segunda.close()
