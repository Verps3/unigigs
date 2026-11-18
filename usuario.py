from dataclasses import dataclass
from enum import Enum


class Rol(str, Enum):
    ESTUDIANTE = "ESTUDIANTE"
    ADMINISTRADOR = "ADMINISTRADOR"


@dataclass
class Usuario:
    """Estudiante (que ofrece o contrata servicios) o administrador."""

    nombre: str
    correo: str
    rol: Rol = Rol.ESTUDIANTE
    id: int | None = None
