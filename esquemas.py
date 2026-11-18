"""Vista (MVC): representación JSON que reciben y devuelven los controladores."""
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.observadores import EventoPedido
from app.models.pago import Pago
from app.models.pedido import Pedido
from app.models.servicio import Servicio
from app.models.usuario import Rol, Usuario

CORREO = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class UsuarioIn(BaseModel):
    nombre: str = Field(min_length=1)
    correo: str = Field(pattern=CORREO)
    rol: Rol = Rol.ESTUDIANTE


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    correo: str
    rol: Rol


class ServicioIn(BaseModel):
    titulo: str = Field(min_length=1)
    descripcion: str = ""
    precio: float = Field(gt=0)
    categoria: str = Field(min_length=1)
    oferente_id: int


class ServicioOut(BaseModel):
    id: int
    titulo: str
    descripcion: str
    precio: float
    categoria: str
    oferente_id: int
    activo: bool


class PedidoIn(BaseModel):
    servicio_id: int
    contratante_id: int


class AccionIn(BaseModel):
    usuario_id: int


class PagoIn(BaseModel):
    usuario_id: int
    metodo: str
    datos: dict[str, str] = {}


class PagoOut(BaseModel):
    metodo: str
    referencia: str
    monto: float
    fecha: datetime


class PedidoOut(BaseModel):
    id: int
    servicio_id: int
    contratante_id: int
    oferente_id: int
    monto: float
    estado: str
    pago: PagoOut | None = None


class NotificacionOut(BaseModel):
    pedido_id: int
    estado_anterior: str
    estado_nuevo: str
    mensaje: str


def a_usuario_out(u: Usuario) -> UsuarioOut:
    return UsuarioOut(id=u.id, nombre=u.nombre, correo=u.correo, rol=u.rol)


def a_servicio_out(s: Servicio) -> ServicioOut:
    return ServicioOut(id=s.id, titulo=s.titulo, descripcion=s.descripcion, precio=s.precio,
                       categoria=s.categoria, oferente_id=s.oferente_id, activo=s.activo)


def a_pago_out(p: Pago) -> PagoOut:
    return PagoOut(metodo=p.metodo, referencia=p.referencia, monto=p.monto, fecha=p.fecha)


def a_pedido_out(p: Pedido) -> PedidoOut:
    return PedidoOut(id=p.id, servicio_id=p.servicio_id, contratante_id=p.contratante_id,
                     oferente_id=p.oferente_id, monto=p.monto, estado=p.estado.nombre,
                     pago=a_pago_out(p.pago) if p.pago else None)


def a_notificacion_out(e: EventoPedido) -> NotificacionOut:
    return NotificacionOut(pedido_id=e.pedido_id, estado_anterior=e.estado_anterior,
                           estado_nuevo=e.estado_nuevo, mensaje=e.mensaje)
