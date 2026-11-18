"""Errores del dominio. El Controlador los traduce a códigos HTTP (ver main.py)."""


class ErrorDeDominio(Exception):
    """Clase base de los errores de negocio."""


class NoEncontradoError(ErrorDeDominio):
    """El recurso solicitado no existe."""


class PermisoDenegadoError(ErrorDeDominio):
    """El usuario no puede ejecutar la acción sobre el recurso."""


class ReglaNegocioError(ErrorDeDominio):
    """Se violó una regla de negocio (datos o contexto inválidos)."""


class TransicionInvalidaError(ErrorDeDominio):
    """La acción no está permitida en el estado actual del pedido (patrón State)."""

    def __init__(self, estado: str, accion: str):
        super().__init__(f"No se puede '{accion}' un pedido en estado '{estado}'.")
        self.estado = estado
        self.accion = accion


class PagoRechazadoError(ErrorDeDominio):
    """El método de pago rechazó la transacción (patrón Strategy)."""
