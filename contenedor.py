from app.models.observadores import BandejaNotificaciones
from app.models.pagos import RegistroMetodosPago
from app.repositories.memoria import RepositorioMemoria


class Contenedor:
    """Raíz de composición: crea y comparte las dependencias de los controladores."""

    def __init__(self) -> None:
        self.usuarios: RepositorioMemoria = RepositorioMemoria("Usuario")
        self.servicios: RepositorioMemoria = RepositorioMemoria("Servicio")
        self.pedidos: RepositorioMemoria = RepositorioMemoria("Pedido")
        self.bandeja = BandejaNotificaciones()
        self.metodos_pago = RegistroMetodosPago()
