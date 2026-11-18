from fastapi import APIRouter

from app.contenedor import Contenedor
from app.excepciones import PermisoDenegadoError, ReglaNegocioError
from app.models.observadores import NotificadorAdmin, NotificadorUsuario
from app.models.pedido import Pedido
from app.views.esquemas import AccionIn, PagoIn, PedidoIn, PedidoOut, a_pedido_out


class PedidoController:
    def __init__(self, contenedor: Contenedor) -> None:
        self.c = contenedor
        self.router = APIRouter(tags=["Pedidos"])
        r = self.router
        r.add_api_route("/pedidos", self.crear, methods=["POST"],
                        response_model=PedidoOut, status_code=201)
        r.add_api_route("/pedidos/{pedido_id}", self.obtener, methods=["GET"],
                        response_model=PedidoOut)
        r.add_api_route("/pedidos/{pedido_id}/contratar", self.contratar, methods=["POST"],
                        response_model=PedidoOut)
        r.add_api_route("/pedidos/{pedido_id}/aceptar", self.aceptar, methods=["POST"],
                        response_model=PedidoOut)
        r.add_api_route("/pedidos/{pedido_id}/rechazar", self.rechazar, methods=["POST"],
                        response_model=PedidoOut)
        r.add_api_route("/pedidos/{pedido_id}/entregar", self.entregar, methods=["POST"],
                        response_model=PedidoOut)
        r.add_api_route("/pedidos/{pedido_id}/cancelar", self.cancelar, methods=["POST"],
                        response_model=PedidoOut)
        r.add_api_route("/pedidos/{pedido_id}/pagar", self.pagar, methods=["POST"],
                        response_model=PedidoOut)
        r.add_api_route("/metodos-pago", self.metodos_pago, methods=["GET"],
                        response_model=list[str])

    # --- casos de uso ---
    def crear(self, datos: PedidoIn) -> PedidoOut:
        servicio = self.c.servicios.obtener(datos.servicio_id)
        contratante = self.c.usuarios.obtener(datos.contratante_id)
        if not servicio.activo:
            raise ReglaNegocioError("El servicio no está disponible.")
        if contratante.id == servicio.oferente_id:
            raise ReglaNegocioError("No puedes contratar tu propio servicio.")
        pedido = self.c.pedidos.agregar(
            Pedido(servicio.id, contratante.id, servicio.oferente_id, servicio.precio))
        pedido.agregar_observador(NotificadorUsuario(pedido.contratante_id, self.c.bandeja))
        pedido.agregar_observador(NotificadorUsuario(pedido.oferente_id, self.c.bandeja))
        pedido.agregar_observador(NotificadorAdmin(self.c.bandeja))
        pedido.publicar()
        return a_pedido_out(pedido)

    def obtener(self, pedido_id: int) -> PedidoOut:
        return a_pedido_out(self.c.pedidos.obtener(pedido_id))

    def contratar(self, pedido_id: int, datos: AccionIn) -> PedidoOut:
        pedido = self._pedido_de(pedido_id, datos.usuario_id, "contratante")
        pedido.contratar()
        return a_pedido_out(pedido)

    def aceptar(self, pedido_id: int, datos: AccionIn) -> PedidoOut:
        pedido = self._pedido_de(pedido_id, datos.usuario_id, "oferente")
        pedido.aceptar()
        return a_pedido_out(pedido)

    def rechazar(self, pedido_id: int, datos: AccionIn) -> PedidoOut:
        pedido = self._pedido_de(pedido_id, datos.usuario_id, "oferente")
        pedido.rechazar()
        return a_pedido_out(pedido)

    def entregar(self, pedido_id: int, datos: AccionIn) -> PedidoOut:
        pedido = self._pedido_de(pedido_id, datos.usuario_id, "oferente")
        pedido.entregar()
        return a_pedido_out(pedido)

    def cancelar(self, pedido_id: int, datos: AccionIn) -> PedidoOut:
        pedido = self._pedido_de(pedido_id, datos.usuario_id, "participante")
        pedido.cancelar()
        return a_pedido_out(pedido)

    def pagar(self, pedido_id: int, datos: PagoIn) -> PedidoOut:
        pedido = self._pedido_de(pedido_id, datos.usuario_id, "contratante")
        metodo = self.c.metodos_pago.obtener(datos.metodo)
        pedido.aprobar_y_pagar(metodo, datos.datos)
        return a_pedido_out(pedido)

    def metodos_pago(self) -> list[str]:
        return self.c.metodos_pago.disponibles()

    # --- auxiliar: valida que el usuario tenga el rol requerido en el pedido ---
    def _pedido_de(self, pedido_id: int, usuario_id: int, rol: str) -> Pedido:
        pedido = self.c.pedidos.obtener(pedido_id)
        self.c.usuarios.obtener(usuario_id)
        permitido = {
            "contratante": usuario_id == pedido.contratante_id,
            "oferente": usuario_id == pedido.oferente_id,
            "participante": usuario_id in (pedido.contratante_id, pedido.oferente_id),
        }[rol]
        if not permitido:
            raise PermisoDenegadoError(f"Esta acción corresponde al {rol} del pedido.")
        return pedido
