from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Pago:
    """Comprobante de un pago aprobado."""

    pedido_id: int
    monto: float
    metodo: str
    referencia: str
    fecha: datetime = field(default_factory=datetime.now)
    id: int | None = None
