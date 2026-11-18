from fastapi import APIRouter

from app.contenedor import Contenedor
from app.models.usuario import Usuario
from app.views.esquemas import (NotificacionOut, UsuarioIn, UsuarioOut,
                                a_notificacion_out, a_usuario_out)


class UsuarioController:
    def __init__(self, contenedor: Contenedor) -> None:
        self.c = contenedor
        self.router = APIRouter(tags=["Usuarios"])
        self.router.add_api_route("/usuarios", self.registrar, methods=["POST"],
                                  response_model=UsuarioOut, status_code=201)
        self.router.add_api_route("/usuarios/{usuario_id}", self.obtener, methods=["GET"],
                                  response_model=UsuarioOut)
        self.router.add_api_route("/usuarios/{usuario_id}/notificaciones", self.notificaciones,
                                  methods=["GET"], response_model=list[NotificacionOut])
        self.router.add_api_route("/admin/notificaciones", self.notificaciones_admin,
                                  methods=["GET"], response_model=list[NotificacionOut])

    def registrar(self, datos: UsuarioIn) -> UsuarioOut:
        usuario = self.c.usuarios.agregar(Usuario(datos.nombre, datos.correo, datos.rol))
        return a_usuario_out(usuario)

    def obtener(self, usuario_id: int) -> UsuarioOut:
        return a_usuario_out(self.c.usuarios.obtener(usuario_id))

    def notificaciones(self, usuario_id: int) -> list[NotificacionOut]:
        self.c.usuarios.obtener(usuario_id)
        return [a_notificacion_out(e) for e in self.c.bandeja.de(f"usuario:{usuario_id}")]

    def notificaciones_admin(self) -> list[NotificacionOut]:
        return [a_notificacion_out(e) for e in self.c.bandeja.de("admin")]
