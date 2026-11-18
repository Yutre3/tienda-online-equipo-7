"""CRUD Peewee de usuarios con eliminación lógica."""

from peewee import IntegrityError

from datos.modelos import PaisModelo, UsuarioModelo
from negocio.entidades import ErrorDominio


class RepositorioUsuarios:
    def guardar(self, usuario: UsuarioModelo) -> UsuarioModelo:
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

    def listar(self, habilitado: bool | None = True) -> list[UsuarioModelo]:
        consulta = UsuarioModelo.select(UsuarioModelo, PaisModelo).join(PaisModelo)
        if habilitado is not None:
            consulta = consulta.where(UsuarioModelo.habilitado == habilitado)
        return list(consulta.order_by(UsuarioModelo.id_usuario))

    def obtener_por_rut(self, rut: str) -> UsuarioModelo | None:
        return (
            UsuarioModelo.select(UsuarioModelo, PaisModelo)
            .join(PaisModelo)
            .where(UsuarioModelo.rut == rut)
            .first()
        )

    def obtener_por_correo(self, correo: str) -> UsuarioModelo | None:
        return (
            UsuarioModelo.select(UsuarioModelo, PaisModelo)
            .join(PaisModelo)
            .where(UsuarioModelo.correo == correo)
            .first()
        )


def listado_usuarios_habilitados() -> list[UsuarioModelo]:
    return RepositorioUsuarios().listar(True)


def listado_usuarios_deshabilitados() -> list[UsuarioModelo]:
    return RepositorioUsuarios().listar(False)


def listado_usuarios() -> list[UsuarioModelo]:
    return RepositorioUsuarios().listar(None)


def obtener_usuario_rut(rut_usuario: str) -> UsuarioModelo | None:
    return RepositorioUsuarios().obtener_por_rut(rut_usuario)


def obtener_usuario_correo(correo_usuario: str) -> UsuarioModelo | None:
    return RepositorioUsuarios().obtener_por_correo(correo_usuario)


def guardar_usuario(usuario: UsuarioModelo) -> UsuarioModelo:
    return RepositorioUsuarios().guardar(usuario)
