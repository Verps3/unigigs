"""Coherencia modelo-código: los diagramas de clases (PlantUML) deben corresponder al código.

Verifica que (1) cada clase del UML existe en el código, (2) cada operación '+metodo()' del UML
existe en esa clase, (3) cada relación de herencia/realización se cumple y (4) cada clase del
código de dominio, controladores, vista y persistencia aparece en algún diagrama.
"""
import importlib
import inspect
import pkgutil
import re
from pathlib import Path

import pytest

import app

DIAGRAMAS = Path(__file__).resolve().parents[1] / "docs" / "diagramas"
ARCHIVOS_CLASES = ["02_clases_dominio_state.puml", "03_clases_strategy.puml",
                   "04_clases_observer.puml", "05_clases_capas_mvc.puml"]
PAQUETES_MODELADOS = ("app.models", "app.controllers", "app.views", "app.repositories",
                      "app.contenedor")

DECLARACION = re.compile(r"^\s*(?:abstract class|abstract|class|interface|enum)\s+(\w+)")
OPERACION = re.compile(r"^\s*\+\s*(\w+)\(")
HERENCIA = re.compile(r"^\s*(\w+)\s*<\|(?:--|\.\.)\s*(\w+)")


def leer_diagramas():
    clases: dict[str, set[str]] = {}
    herencias: list[tuple[str, str]] = []
    for archivo in ARCHIVOS_CLASES:
        actual = None
        for linea in (DIAGRAMAS / archivo).read_text(encoding="utf-8").splitlines():
            if (m := DECLARACION.match(linea)):
                actual = m.group(1)
                clases.setdefault(actual, set())
                if not linea.rstrip().endswith("{"):
                    actual = None
                continue
            if actual and linea.strip() == "}":
                actual = None
            elif actual and (m := OPERACION.match(linea)):
                clases[actual].add(m.group(1))
            elif (m := HERENCIA.match(linea)):
                herencias.append((m.group(1), m.group(2)))
    return clases, herencias


def clases_del_codigo():
    encontradas = {}
    for info in pkgutil.walk_packages(app.__path__, "app."):
        if not info.name.startswith(PAQUETES_MODELADOS):
            continue
        modulo = importlib.import_module(info.name)
        for nombre, obj in inspect.getmembers(modulo, inspect.isclass):
            if obj.__module__ == modulo.__name__:
                encontradas[nombre] = obj
    return encontradas


CLASES_UML, HERENCIAS_UML = leer_diagramas()
CODIGO = clases_del_codigo()


@pytest.mark.parametrize("nombre", sorted(CLASES_UML))
def test_clase_del_uml_existe_en_el_codigo(nombre):
    assert nombre in CODIGO, f"La clase UML '{nombre}' no existe en el código"


@pytest.mark.parametrize("nombre", sorted(n for n in CLASES_UML if CLASES_UML[n]))
def test_operaciones_del_uml_existen_en_el_codigo(nombre):
    for operacion in CLASES_UML[nombre]:
        assert hasattr(CODIGO[nombre], operacion), f"{nombre}.{operacion}() no existe en el código"


@pytest.mark.parametrize("padre,hijo", HERENCIAS_UML)
def test_herencia_del_uml_se_cumple_en_el_codigo(padre, hijo):
    assert issubclass(CODIGO[hijo], CODIGO[padre]), f"{hijo} no hereda de {padre}"


def test_todas_las_clases_del_codigo_estan_en_el_uml():
    faltantes = sorted(set(CODIGO) - set(CLASES_UML))
    assert not faltantes, f"Clases del código sin diagrama: {faltantes}"
