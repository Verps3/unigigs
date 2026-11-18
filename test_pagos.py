"""Patrón Strategy: métodos de pago intercambiables bajo la misma interfaz."""
import pytest

from app.excepciones import PagoRechazadoError, ReglaNegocioError
from app.models.pagos import MetodoPago, PagoNequi, PagoPSE, PagoTarjeta, RegistroMetodosPago
from app.models.pedido import Pedido


@pytest.mark.parametrize("metodo,datos", [
    (PagoTarjeta(), {"ultimos4": "1234"}),
    (PagoPSE(), {"banco": "Davivienda"}),
    (PagoNequi(), {"celular": "3001234567"}),
])
def test_estrategias_aprueban_con_datos_validos(metodo, datos):
    assert isinstance(metodo, MetodoPago)
    r = metodo.procesar_pago(10000, datos)
    assert r.aprobado and r.referencia and r.metodo == metodo.nombre


@pytest.mark.parametrize("metodo", [PagoTarjeta(), PagoPSE(), PagoNequi()])
def test_estrategias_rechazan_sin_datos(metodo):
    assert not metodo.procesar_pago(10000, {}).aprobado


def test_registro_devuelve_estrategia_y_rechaza_desconocidas():
    registro = RegistroMetodosPago()
    assert registro.disponibles() == ["NEQUI", "PSE", "TARJETA"]
    assert isinstance(registro.obtener("nequi"), PagoNequi)
    with pytest.raises(ReglaNegocioError):
        registro.obtener("BITCOIN")


def test_pago_rechazado_mantiene_estado_entregado():
    p = Pedido(1, 2, 3, 20000)
    p.id = 1
    p.contratar(); p.aceptar(); p.entregar()
    with pytest.raises(PagoRechazadoError):
        p.aprobar_y_pagar(PagoNequi(), {"celular": "123"})
    assert p.estado.nombre == "Entregado" and p.pago is None
