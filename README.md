# UniGigs

Marketplace web de servicios y proyectos simples entre estudiantes universitarios.
Proyecto de **Lenguajes de Modelado** (Fundación Universitaria Compensar, Ingeniería de Sistemas).

El código es **coherente con el modelado UML y C4** de `docs/diagramas/`; una prueba automática
(`tests/test_coherencia_uml.py`) compara los diagramas de clases con el código.

## Tecnología
Python 3.12 · FastAPI · Pydantic · pytest. Persistencia **en memoria** (prototipo).

## Ejecutar
```bash
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Abrir http://127.0.0.1:8000/docs (Swagger UI) para probar la API.

## Pruebas
```bash
python -m pytest -q
```

## Arquitectura (MVC) y patrones
| Elemento UML | Código |
|---|---|
| **Modelo** (MVC): `Usuario`, `Servicio`, `Pedido`, `Pago` | `app/models/` |
| **Vista** (MVC): esquemas JSON de entrada y salida | `app/views/esquemas.py` |
| **Controlador** (MVC): `UsuarioController`, `ServicioController`, `PedidoController` | `app/controllers/` |
| **Patrón State**: `EstadoPedido` y sus 6 estados | `app/models/estados.py` |
| **Patrón Strategy**: `MetodoPago`, `PagoTarjeta`, `PagoPSE`, `PagoNequi` | `app/models/pagos.py` |
| **Patrón Observer**: `Observer`, `NotificadorUsuario`, `NotificadorAdmin` | `app/models/observadores.py` |
| Repositorio y composición: `RepositorioMemoria`, `Contenedor` | `app/repositories/`, `app/contenedor.py` |

## Flujo principal de la API
1. `POST /usuarios` (oferente, contratante) y `POST /servicios` (publicar servicio).
2. `POST /pedidos` → estado **Publicado**.
3. `POST /pedidos/{id}/contratar` (contratante) → **Contratado**.
4. `POST /pedidos/{id}/aceptar` (oferente) → **En progreso**.
5. `POST /pedidos/{id}/entregar` (oferente) → **Entregado**.
6. `POST /pedidos/{id}/pagar` (contratante, con `metodo` = `TARJETA`, `PSE` o `NEQUI`) → **Pagado**.
7. `GET /usuarios/{id}/notificaciones` y `GET /admin/notificaciones` muestran los avisos (Observer).

Códigos de error: 403 (rol sin permiso), 404 (no existe), 409 (transición inválida del estado),
402 (pago rechazado), 422 (regla de negocio o datos inválidos).

## Diagramas (`docs/diagramas/`)
Fuentes editables en PlantUML (`.puml`) e imágenes (`.png`): casos de uso, clases (dominio y State,
Strategy, Observer, capas MVC), despliegue, estados, secuencias y modelo C4 (contexto, contenedores
y componentes). Para regenerarlos: `java -jar plantuml.jar -tpng docs/diagramas/*.puml`.

## Alcance y limitaciones
Prototipo académico: sin autenticación real (las acciones reciben `usuario_id`), pagos simulados,
datos en memoria (se pierden al reiniciar) y sin interfaz web propia (se usa Swagger UI).

## Autores
Juan David Méndez Díaz · Nicolás Rodríguez Cáceres. Docente: John Fredy Céspedes Beltrán.
