import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.v1.agencia_router import router as agencia_router
from app.core.config import settings
from app.core.exception_handler import register_exception_handlers
from app.api.v1.producto_router import router as producto_router
from app.api.v1.guia_router import router as guia_router
from app.api.v1.liquidacion_router import router as liquidacion_router
from app.api.v1.cobranza_router import router as cobranza_router
from app.api.v1.inventario_router import router as inventario_router
from app.api.v1.reporte_router import router as reporte_router
from app.api.v1.auth_router import router as auth_router
from app.api.v1.usuario_router import router as usuario_router
from app.db.session import SessionLocal
from app.repositories.guia_repository import GuiaRepository
from app.services.bootstrap_service import crear_admin_inicial

logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
logger = logging.getLogger("sidec")


def _actualizar_guias_vencidas() -> int:
    with SessionLocal() as db:
        return GuiaRepository(db).actualizar_guias_pendientes_vencidas()


async def actualizar_estados_guias_periodicamente() -> None:
    while True:
        # Un fallo puntual (p. ej. la base reiniciándose) no debe matar la tarea:
        # sin el try, la excepción la termina en silencio y no vuelve a correr.
        try:
            # La consulta es síncrona: en un hilo para no bloquear el event loop.
            actualizadas = await asyncio.to_thread(_actualizar_guias_vencidas)
            logger.info("Guías vencidas pasadas a PENDIENTE_LIQUIDACION: %s", actualizadas)
        except Exception:
            logger.exception("No se pudieron actualizar las guías vencidas; se reintenta en 24 h.")

        await asyncio.sleep(24 * 60 * 60)


def _crear_admin_inicial() -> None:
    with SessionLocal() as db:
        crear_admin_inicial(db)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await asyncio.to_thread(_crear_admin_inicial)
    tarea_actualizacion = asyncio.create_task(
        actualizar_estados_guias_periodicamente()
    )
    try:
        yield
    finally:
        tarea_actualizacion.cancel()
        with suppress(asyncio.CancelledError):
            await tarea_actualizacion

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    root_path=settings.API_ROOT_PATH,
    lifespan=lifespan,
)
register_exception_handlers(app)


@app.get("/health", include_in_schema=False)
def health():
    """Liveness: el proceso responde. No toca la base para no reiniciar el pod si ella cae."""
    return {"status": "ok"}


@app.get("/health/ready", include_in_schema=False)
def health_ready():
    """Readiness: el pod solo recibe tráfico si la base responde."""
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(status_code=503, content={"status": "db_unavailable"})
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(usuario_router)
app.include_router(agencia_router)
app.include_router(producto_router)
app.include_router(guia_router)
app.include_router(liquidacion_router)
app.include_router(cobranza_router)
app.include_router(inventario_router)
app.include_router(reporte_router)
