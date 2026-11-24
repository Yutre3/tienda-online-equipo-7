"""Funciones Peewee para usuarios y su baja lógica."""

from peewee import IntegrityError, SqliteDatabase

from datos.conexion import base_datos_proxy, transaccion_escritura
from datos.modelos import PaisModelo, UsuarioModelo
from negocio.entidades import ErrorDominio


def guardar_usuario(usuario: UsuarioModelo) -> UsuarioModelo:
    duplicado = UsuarioModelo.select().where(
        (UsuarioModelo.rut == usuario.rut)
        | (UsuarioModelo.correo == usuario.correo)
    )
    if usuario.id_usuario is not None:
        duplicado = duplicado.where(
            UsuarioModelo.id_usuario != usuario.id_usuario
        )
    if duplicado.first() is not None:
        raise ErrorDominio(
            "Ya existe otro usuario con el mismo RUT o correo."
        )
    try:
        usuario.save(force_insert=usuario.id_usuario is None)
    except IntegrityError as error:
        raise ErrorDominio(
            "Ya existe otro usuario con el mismo RUT o correo."
        ) from error
    return usuario


def guardar_primer_usuario(usuario: UsuarioModelo) -> UsuarioModelo:
    """Inserta una única cuenta inicial bajo un bloqueo de escritura."""
    with transaccion_escritura():
        base = base_datos_proxy.obj
        if isinstance(base, SqliteDatabase):
            existe_usuario = cantidad_usuarios() > 0
        else:
            # Todas las instalaciones tienen un país antes del alta inicial.
            # Bloquear siempre la primera fila entrega el mismo mutex en MySQL.
            PaisModelo.select(PaisModelo.id_pais).order_by(
                PaisModelo.id_pais
            ).for_update().get()
            existe_usuario = (
                UsuarioModelo.select(UsuarioModelo.id_usuario)
                .for_update()
                .first()
                is not None
            )
        if existe_usuario:
            raise ErrorDominio(
                "La preparación del primer usuario solo está disponible "
                "durante la instalación inicial."
            )
        return guardar_usuario(usuario)


def actualizar_password_usuario(
    usuario: UsuarioModelo, password: str
) -> UsuarioModelo:
    """Actualiza solo el hash sin sobrescribir cambios concurrentes."""
    usuario.password = password
    usuario.save(only=[UsuarioModelo.password])
    return UsuarioModelo.get_by_id(usuario.id_usuario)


def _listado(habilitado: bool | None) -> list[UsuarioModelo]:
    consulta = UsuarioModelo.select(UsuarioModelo, PaisModelo).join(PaisModelo)
    if habilitado is not None:
        consulta = consulta.where(UsuarioModelo.habilitado == habilitado)
    return list(consulta.order_by(UsuarioModelo.id_usuario))


def listado_usuarios_habilitados() -> list[UsuarioModelo]:
    return _listado(True)


def listado_usuarios_deshabilitados() -> list[UsuarioModelo]:
    return _listado(False)


def listado_usuarios() -> list[UsuarioModelo]:
    return _listado(None)


def obtener_usuario_rut(rut_usuario: str) -> UsuarioModelo | None:
    return (
        UsuarioModelo.select(UsuarioModelo, PaisModelo)
        .join(PaisModelo)
        .where(UsuarioModelo.rut == rut_usuario)
        .first()
    )


def obtener_usuario_correo(correo_usuario: str) -> UsuarioModelo | None:
    return (
        UsuarioModelo.select(UsuarioModelo, PaisModelo)
        .join(PaisModelo)
        .where(UsuarioModelo.correo == correo_usuario)
        .first()
    )


def cantidad_usuarios() -> int:
    return UsuarioModelo.select().count()
