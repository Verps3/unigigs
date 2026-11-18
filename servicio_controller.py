from fastapi import APIRouter

from app.contenedor import Contenedor
from app.excepciones import PermisoDenegadoError
from app.models.servicio import Servicio
from app.models.usuario import Rol
from app.views.esquemas import AccionIn, ServicioIn, ServicioOut, a_servicio_out


class ServicioController:
    def __init__(self, contenedor: Contenedor) -> None:
        self.c = contenedor
        self.router = APIRouter(tags=["Servicios"])
        self.router.add_api_route("/servicios", self.publicar, methods=["POST"],
                                  response_model=ServicioOut, status_code=201)
        self.router.add_api_route("/servicios", self.buscar, methods=["GET"],
                                  response_model=list[ServicioOut])
        self.router.add_api_route("/servicios/{servicio_id}", self.obtener, methods=["GET"],
                                  response_model=ServicioOut)
        self.router.add_api_route("/servicios/{servicio_id}/desactivar", self.desactivar,
                                  methods=["POST"], response_model=ServicioOut)

    def publicar(self, datos: ServicioIn) -> ServicioOut:
        self.c.usuarios.obtener(datos.oferente_id)
        servicio = Servicio(datos.titulo, datos.descripcion, datos.precio,
                            datos.categoria, datos.oferente_id)
        return a_servicio_out(self.c.servicios.agregar(servicio))

    def buscar(self, categoria: str | None = None, q: str | None = None) -> list[ServicioOut]:
        resultado = [s for s in self.c.servicios.listar() if s.activo]
        if categoria:
            resultado = [s for s in resultado if s.categoria.lower() == categoria.lower()]
        if q:
            resultado = [s for s in resultado
                         if q.lower() in f"{s.titulo} {s.descripcion}".lower()]
        return [a_servicio_out(s) for s in resultado]

    def obtener(self, servicio_id: int) -> ServicioOut:
        return a_servicio_out(self.c.servicios.obtener(servicio_id))

    def desactivar(self, servicio_id: int, datos: AccionIn) -> ServicioOut:
        servicio = self.c.servicios.obtener(servicio_id)
        usuario = self.c.usuarios.obtener(datos.usuario_id)
        if usuario.id != servicio.oferente_id and usuario.rol != Rol.ADMINISTRADOR:
            raise PermisoDenegadoError("Solo el oferente o un administrador puede desactivarlo.")
        servicio.desactivar()
        return a_servicio_out(servicio)
