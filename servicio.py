from dataclasses import dataclass

from app.excepciones import ReglaNegocioError


@dataclass
class Servicio:
    """Servicio publicado por un estudiante (el que ofrece)."""

    titulo: str
    descripcion: str
    precio: float
    categoria: str
    oferente_id: int
    activo: bool = True
    id: int | None = None

    def __post_init__(self) -> None:
        if self.precio <= 0:
            raise ReglaNegocioError("El precio del servicio debe ser mayor que cero.")

    def desactivar(self) -> None:
        self.activo = False
