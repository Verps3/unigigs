"""Patrón Observer: el Pedido (Subject) avisa a sus observadores cuando cambia."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class EventoPedido:
    pedido_id: int
    estado_anterior: str
    estado_nuevo: str
    mensaje: str
    fecha: datetime = field(default_factory=datetime.now)


class BandejaNotificaciones:
    """Almacena las notificaciones por destinatario ('usuario:<id>' o 'admin')."""

    def __init__(self) -> None:
        self._bandejas: dict[str, list[EventoPedido]] = {}

    def agregar(self, destinatario: str, evento: EventoPedido) -> None:
        self._bandejas.setdefault(destinatario, []).append(evento)

    def de(self, destinatario: str) -> list[EventoPedido]:
        return list(self._bandejas.get(destinatario, []))


class Observer(ABC):
    @abstractmethod
    def actualizar(self, evento: EventoPedido) -> None:
        """Reacciona al cambio ocurrido en el Pedido."""


class NotificadorUsuario(Observer):
    """Avisa a un estudiante (el que ofrece o el que contrata)."""

    def __init__(self, usuario_id: int, bandeja: BandejaNotificaciones) -> None:
        self.usuario_id = usuario_id
        self.bandeja = bandeja

    def actualizar(self, evento: EventoPedido) -> None:
        self.bandeja.agregar(f"usuario:{self.usuario_id}", evento)


class NotificadorAdmin(Observer):
    """Avisa al administrador de la plataforma."""

    def __init__(self, bandeja: BandejaNotificaciones) -> None:
        self.bandeja = bandeja

    def actualizar(self, evento: EventoPedido) -> None:
        self.bandeja.agregar("admin", evento)
