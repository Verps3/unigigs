from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.contenedor import Contenedor
from app.controllers.pedido_controller import PedidoController
from app.controllers.servicio_controller import ServicioController
from app.controllers.usuario_controller import UsuarioController
from app.excepciones import (ErrorDeDominio, NoEncontradoError, PagoRechazadoError,
                             PermisoDenegadoError, ReglaNegocioError, TransicionInvalidaError)

CODIGOS_HTTP = {
    NoEncontradoError: 404,
    PermisoDenegadoError: 403,
    TransicionInvalidaError: 409,
    PagoRechazadoError: 402,
    ReglaNegocioError: 422,
}


def crear_app(contenedor: Contenedor | None = None) -> FastAPI:
    contenedor = contenedor or Contenedor()
    app = FastAPI(title="UniGigs API",
                  description="Marketplace de servicios entre estudiantes universitarios.",
                  version="1.0.0")

    @app.exception_handler(ErrorDeDominio)
    async def manejar_error_de_dominio(_: Request, error: ErrorDeDominio) -> JSONResponse:
        codigo = CODIGOS_HTTP.get(type(error), 400)
        return JSONResponse(status_code=codigo, content={"detalle": str(error)})

    for controlador in (UsuarioController(contenedor), ServicioController(contenedor),
                        PedidoController(contenedor)):
        app.include_router(controlador.router)
    return app


app = crear_app()
