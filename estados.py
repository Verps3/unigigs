"""Patrón State: cada estado del Pedido decide qué acciones permite."""
from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from app.excepciones import PagoRechazadoError, TransicionInvalidaError
from app.models.pago import Pago
from app.models.pagos import MetodoPago

if TYPE_CHECKING:
    from app.models.pedido import Pedido


class EstadoPedido(ABC):
    """Por defecto toda acción es inválida; cada estado concreto sobrescribe las que permite."""

    nombre: str = ""

    def contratar(self, pedido: Pedido) -> None:
        raise TransicionInvalidaError(self.nombre, "contratar")

    def aceptar(self, pedido: Pedido) -> None:
        raise TransicionInvalidaError(self.nombre, "aceptar")

    def rechazar(self, pedido: Pedido) -> None:
        raise TransicionInvalidaError(self.nombre, "rechazar")

    def entregar(self, pedido: Pedido) -> None:
        raise TransicionInvalidaError(self.nombre, "entregar")

    def cancelar(self, pedido: Pedido) -> None:
        raise TransicionInvalidaError(self.nombre, "cancelar")

    def aprobar_y_pagar(self, pedido: Pedido, metodo: MetodoPago, datos: dict[str, str]) -> None:
        raise TransicionInvalidaError(self.nombre, "pagar")


class Publicado(EstadoPedido):
    nombre = "Publicado"

    def contratar(self, pedido: Pedido) -> None:
        pedido.cambiar_estado(Contratado())


class Contratado(EstadoPedido):
    nombre = "Contratado"

    def aceptar(self, pedido: Pedido) -> None:
        pedido.cambiar_estado(EnProgreso())

    def rechazar(self, pedido: Pedido) -> None:
        pedido.cambiar_estado(Cancelado())


class EnProgreso(EstadoPedido):
    nombre = "En progreso"

    def entregar(self, pedido: Pedido) -> None:
        pedido.cambiar_estado(Entregado())

    def cancelar(self, pedido: Pedido) -> None:
        pedido.cambiar_estado(Cancelado())


class Entregado(EstadoPedido):
    nombre = "Entregado"

    def aprobar_y_pagar(self, pedido: Pedido, metodo: MetodoPago, datos: dict[str, str]) -> None:
        resultado = metodo.procesar_pago(pedido.monto, datos)  # Strategy
        if not resultado.aprobado:
            raise PagoRechazadoError(resultado.mensaje or "Pago rechazado.")
        pedido.pago = Pago(pedido.id, pedido.monto, resultado.metodo, resultado.referencia)
        pedido.cambiar_estado(Pagado())


class Pagado(EstadoPedido):
    nombre = "Pagado"


class Cancelado(EstadoPedido):
    nombre = "Cancelado"
