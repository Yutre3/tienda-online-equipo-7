"""Compatibilidad con el repositorio funcional de usuarios."""

from datos.modelos import UsuarioModelo
from datos.repositorio.usuarios import (
    cantidad_usuarios,
    guardar_usuario,
    listado_usuarios,
    listado_usuarios_deshabilitados,
    listado_usuarios_habilitados,
    obtener_usuario_correo,
    obtener_usuario_rut,
)


class RepositorioUsuarios:
    def guardar(self, usuario: UsuarioModelo) -> UsuarioModelo:
        return guardar_usuario(usuario)

    def listar(self, habilitado: bool | None = True) -> list[UsuarioModelo]:
        if habilitado is True:
            return listado_usuarios_habilitados()
        if habilitado is False:
            return listado_usuarios_deshabilitados()
        return listado_usuarios()

    def obtener_por_rut(self, rut: str) -> UsuarioModelo | None:
        return obtener_usuario_rut(rut)

    def obtener_por_correo(self, correo: str) -> UsuarioModelo | None:
        return obtener_usuario_correo(correo)


__all__ = [
    "RepositorioUsuarios",
    "cantidad_usuarios",
    "guardar_usuario",
    "listado_usuarios",
    "listado_usuarios_deshabilitados",
    "listado_usuarios_habilitados",
    "obtener_usuario_correo",
    "obtener_usuario_rut",
]
