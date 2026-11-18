"""Patrón Observer: el Pedido notifica a sus observadores en cada cambio."""
from app.models.observadores import (BandejaNotificaciones, NotificadorAdmin,
                                     NotificadorUsuario, Observer)
from app.models.pedido import Pedido


def pedido_con_observadores():
    bandeja = BandejaNotificaciones()
    p = Pedido(1, 2, 3, 30000)
    p.id = 7
    p.agregar_observador(NotificadorUsuario(2, bandeja))
    p.agregar_observador(NotificadorUsuario(3, bandeja))
    p.agregar_observador(NotificadorAdmin(bandeja))
    return p, bandeja


def test_notificadores_son_observers():
    assert issubclass(NotificadorUsuario, Observer) and issubclass(NotificadorAdmin, Observer)


def test_cada_cambio_llega_a_todos_los_interesados():
    p, bandeja = pedido_con_observadores()
    p.publicar()
    p.contratar()
    for destinatario in ("usuario:2", "usuario:3", "admin"):
        eventos = bandeja.de(destinatario)
        assert [e.estado_nuevo for e in eventos] == ["Publicado", "Contratado"]


def test_quitar_observador_deja_de_notificar():
    p, bandeja = pedido_con_observadores()
    admin = p._observadores[2]
    p.quitar_observador(admin)
    p.contratar()
    assert bandeja.de("admin") == []
    assert len(bandeja.de("usuario:2")) == 1
