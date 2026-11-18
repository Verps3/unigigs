"""Pruebas de integración: flujo completo a través de los controladores."""
import pytest
from fastapi.testclient import TestClient

from app.contenedor import Contenedor
from app.main import crear_app


@pytest.fixture
def cliente():
    return TestClient(crear_app(Contenedor()))


@pytest.fixture
def escenario(cliente):
    """Crea oferente (1), contratante (2), administrador (3) y un servicio (1)."""
    cliente.post("/usuarios", json={"nombre": "Ana", "correo": "ana@u.co"})
    cliente.post("/usuarios", json={"nombre": "Beto", "correo": "beto@u.co"})
    cliente.post("/usuarios", json={"nombre": "Admin", "correo": "adm@u.co", "rol": "ADMINISTRADOR"})
    cliente.post("/servicios", json={"titulo": "Logo", "descripcion": "Diseño de logo",
                                     "precio": 80000, "categoria": "Diseño", "oferente_id": 1})
    return cliente


def accion(c, pedido, ruta, usuario, **extra):
    return c.post(f"/pedidos/{pedido}/{ruta}", json={"usuario_id": usuario, **extra})


def test_flujo_feliz_completo(escenario):
    c = escenario
    r = c.post("/pedidos", json={"servicio_id": 1, "contratante_id": 2})
    assert r.status_code == 201 and r.json()["estado"] == "Publicado" and r.json()["monto"] == 80000
    assert accion(c, 1, "contratar", 2).json()["estado"] == "Contratado"
    assert accion(c, 1, "aceptar", 1).json()["estado"] == "En progreso"
    assert accion(c, 1, "entregar", 1).json()["estado"] == "Entregado"
    r = accion(c, 1, "pagar", 2, metodo="PSE", datos={"banco": "Bancolombia"})
    assert r.status_code == 200 and r.json()["estado"] == "Pagado"
    assert r.json()["pago"]["referencia"].startswith("PSE-")


def test_notificaciones_llegan_a_oferente_contratante_y_admin(escenario):
    c = escenario
    c.post("/pedidos", json={"servicio_id": 1, "contratante_id": 2})
    accion(c, 1, "contratar", 2)
    for ruta in ("/usuarios/1/notificaciones", "/usuarios/2/notificaciones", "/admin/notificaciones"):
        estados = [n["estado_nuevo"] for n in c.get(ruta).json()]
        assert estados == ["Publicado", "Contratado"]


def test_transicion_invalida_devuelve_409(escenario):
    c = escenario
    c.post("/pedidos", json={"servicio_id": 1, "contratante_id": 2})
    assert accion(c, 1, "entregar", 1).status_code == 409


def test_permisos_devuelven_403(escenario):
    c = escenario
    c.post("/pedidos", json={"servicio_id": 1, "contratante_id": 2})
    assert accion(c, 1, "contratar", 1).status_code == 403       # el oferente no contrata
    accion(c, 1, "contratar", 2)
    assert accion(c, 1, "aceptar", 2).status_code == 403         # el contratante no acepta
    assert accion(c, 1, "aceptar", 3).status_code == 403         # un tercero tampoco


def test_pago_rechazado_devuelve_402(escenario):
    c = escenario
    c.post("/pedidos", json={"servicio_id": 1, "contratante_id": 2})
    accion(c, 1, "contratar", 2); accion(c, 1, "aceptar", 1); accion(c, 1, "entregar", 1)
    r = accion(c, 1, "pagar", 2, metodo="NEQUI", datos={})
    assert r.status_code == 402
    assert c.get("/pedidos/1").json()["estado"] == "Entregado"


def test_reglas_de_negocio_y_recursos_inexistentes(escenario):
    c = escenario
    assert c.post("/pedidos", json={"servicio_id": 1, "contratante_id": 1}).status_code == 422
    assert c.post("/pedidos", json={"servicio_id": 99, "contratante_id": 2}).status_code == 404
    c.post("/pedidos", json={"servicio_id": 1, "contratante_id": 2})
    accion(c, 1, "contratar", 2); accion(c, 1, "aceptar", 1); accion(c, 1, "entregar", 1)
    assert accion(c, 1, "pagar", 2, metodo="BITCOIN").status_code == 422
    assert c.post("/servicios", json={"titulo": "X", "precio": -5, "categoria": "a",
                                      "oferente_id": 1}).status_code == 422


def test_buscar_y_desactivar_servicio(escenario):
    c = escenario
    assert len(c.get("/servicios", params={"categoria": "diseño"}).json()) == 1
    assert len(c.get("/servicios", params={"q": "logo"}).json()) == 1
    assert c.post("/servicios/1/desactivar", json={"usuario_id": 2}).status_code == 403
    assert c.post("/servicios/1/desactivar", json={"usuario_id": 3}).status_code == 200  # admin
    assert c.get("/servicios").json() == []
    assert c.post("/pedidos", json={"servicio_id": 1, "contratante_id": 2}).status_code == 422
