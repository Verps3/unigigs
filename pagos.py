"""Patrón Strategy: cada método de pago es una estrategia intercambiable."""
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.excepciones import ReglaNegocioError


@dataclass(frozen=True)
class ResultadoPago:
    aprobado: bool
    metodo: str
    referencia: str = ""
    mensaje: str = ""


class MetodoPago(ABC):
    nombre: str = ""

    @abstractmethod
    def procesar_pago(self, monto: float, datos: dict[str, str]) -> ResultadoPago:
        """Procesa el pago (simulado en el prototipo) y devuelve el resultado."""

    def _referencia(self, prefijo: str) -> str:
        return f"{prefijo}-{uuid.uuid4().hex[:8].upper()}"


class PagoTarjeta(MetodoPago):
    nombre = "TARJETA"

    def procesar_pago(self, monto: float, datos: dict[str, str]) -> ResultadoPago:
        ultimos4 = datos.get("ultimos4", "")
        if not (ultimos4.isdigit() and len(ultimos4) == 4):
            return ResultadoPago(False, self.nombre, mensaje="Falta 'ultimos4' (4 dígitos).")
        return ResultadoPago(True, self.nombre, self._referencia("TAR"))


class PagoPSE(MetodoPago):
    nombre = "PSE"

    def procesar_pago(self, monto: float, datos: dict[str, str]) -> ResultadoPago:
        if not datos.get("banco"):
            return ResultadoPago(False, self.nombre, mensaje="Falta 'banco'.")
        return ResultadoPago(True, self.nombre, self._referencia("PSE"))


class PagoNequi(MetodoPago):
    nombre = "NEQUI"

    def procesar_pago(self, monto: float, datos: dict[str, str]) -> ResultadoPago:
        celular = datos.get("celular", "")
        if not (celular.isdigit() and len(celular) == 10):
            return ResultadoPago(False, self.nombre, mensaje="Falta 'celular' (10 dígitos).")
        return ResultadoPago(True, self.nombre, self._referencia("NEQ"))


class RegistroMetodosPago:
    """Catálogo de estrategias disponibles. Agregar un método = registrar una clase nueva."""

    def __init__(self) -> None:
        self._metodos: dict[str, MetodoPago] = {}
        for metodo in (PagoTarjeta(), PagoPSE(), PagoNequi()):
            self._metodos[metodo.nombre] = metodo

    def obtener(self, nombre: str) -> MetodoPago:
        try:
            return self._metodos[nombre.upper()]
        except KeyError:
            raise ReglaNegocioError(f"Método de pago no disponible: '{nombre}'.") from None

    def disponibles(self) -> list[str]:
        return sorted(self._metodos)
