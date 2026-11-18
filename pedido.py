from datetime import datetime

from app.models.estados import EstadoPedido, Publicado
from app.models.observadores import EventoPedido, Observer
from app.models.pago import Pago
from app.models.pagos import MetodoPago


class Pedido:
    """Contexto del patrón State y Subject del patrón Observer."""

    def __init__(self, servicio_id: int, contratante_id: int, oferente_id: int, monto: float) -> None:
        self.id: int | None = None
        self.servicio_id = servicio_id
        self.contratante_id = contratante_id
        self.oferente_id = oferente_id
        self.monto = monto
        self.fecha = datetime.now()
        self.pago: Pago | None = None
        self._estado: EstadoPedido = Publicado()
        self._observadores: list[Observer] = []

    # --- Observer (Subject) ---
    def agregar_observador(self, observador: Observer) -> None:
        self._observadores.append(observador)

    def quitar_observador(self, observador: Observer) -> None:
        self._observadores.remove(observador)

    def notificar(self, evento: EventoPedido) -> None:
        for observador in self._observadores:
            observador.actualizar(evento)

    # --- State (Context) ---
    @property
    def estado(self) -> EstadoPedido:
        return self._estado

    def cambiar_estado(self, nuevo: EstadoPedido) -> None:
        anterior = self._estado.nombre
        self._estado = nuevo
        self.notificar(EventoPedido(self.id, anterior, nuevo.nombre,
                                    f"Pedido #{self.id}: {anterior} -> {nuevo.nombre}"))

    def publicar(self) -> None:
        self.notificar(EventoPedido(self.id, "", self._estado.nombre,
                                    f"Pedido #{self.id}: publicado"))

    def contratar(self) -> None:
        self._estado.contratar(self)

    def aceptar(self) -> None:
        self._estado.aceptar(self)

    def rechazar(self) -> None:
        self._estado.rechazar(self)

    def entregar(self) -> None:
        self._estado.entregar(self)

    def cancelar(self) -> None:
        self._estado.cancelar(self)

    def aprobar_y_pagar(self, metodo: MetodoPago, datos: dict[str, str]) -> None:
        self._estado.aprobar_y_pagar(self, metodo, datos)
