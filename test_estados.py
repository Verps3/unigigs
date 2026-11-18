"""Patrón State: transiciones permitidas e inválidas del Pedido."""
import pytest

from app.excepciones import TransicionInvalidaError
from app.models.pagos import PagoPSE
from app.models.pedido import Pedido


def nuevo_pedido() -> Pedido:
    p = Pedido(servicio_id=1, contratante_id=2, oferente_id=3, monto=50000)
    p.id = 1
    return p


def test_flujo_completo_hasta_pagado():
    p = nuevo_pedido()
    assert p.estado.nombre == "Publicado"
    p.contratar()
    assert p.estado.nombre == "Contratado"
    p.aceptar()
    assert p.estado.nombre == "En progreso"
    p.entregar()
    assert p.estado.nombre == "Entregado"
    p.aprobar_y_pagar(PagoPSE(), {"banco": "Bancolombia"})
    assert p.estado.nombre == "Pagado"
    assert p.pago is not None and p.pago.monto == 50000


def test_rechazar_desde_contratado_cancela():
    p = nuevo_pedido()
    p.contratar()
    p.rechazar()
    assert p.estado.nombre == "Cancelado"


def test_cancelar_desde_en_progreso():
    p = nuevo_pedido()
    p.contratar()
    p.aceptar()
    p.cancelar()
    assert p.estado.nombre == "Cancelado"


@pytest.mark.parametrize("accion", ["aceptar", "entregar", "rechazar", "cancelar"])
def test_acciones_invalidas_en_publicado(accion):
    p = nuevo_pedido()
    with pytest.raises(TransicionInvalidaError):
        getattr(p, accion)()
    assert p.estado.nombre == "Publicado"


def test_no_se_puede_pagar_algo_no_entregado():
    p = nuevo_pedido()
    p.contratar()
    p.aceptar()
    with pytest.raises(TransicionInvalidaError):
        p.aprobar_y_pagar(PagoPSE(), {"banco": "X"})
    assert p.pago is None


@pytest.mark.parametrize("estado_final", ["Pagado", "Cancelado"])
def test_estados_finales_no_aceptan_acciones(estado_final):
    p = nuevo_pedido()
    p.contratar()
    if estado_final == "Cancelado":
        p.rechazar()
    else:
        p.aceptar()
        p.entregar()
        p.aprobar_y_pagar(PagoPSE(), {"banco": "X"})
    for accion in ("contratar", "aceptar", "rechazar", "entregar", "cancelar"):
        with pytest.raises(TransicionInvalidaError):
            getattr(p, accion)()
