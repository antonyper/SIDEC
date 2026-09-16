import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI

from app.api.v1.agencia_router import router as agencia_router
from app.core.config import settings
from app.core.exception_handler import register_exception_handlers
from app.api.v1.producto_router import router as producto_router
from app.api.v1.guia_router import router as guia_router
from app.api.v1.liquidacion_router import router as liquidacion_router
from app.api.v1.cobranza_router import router as cobranza_router
from app.api.v1.inventario_router import router as inventario_router
from app.api.v1.reporte_router import router as reporte_router
from app.db.session import SessionLocal
from app.repositories.guia_repository import GuiaRepository


async def actualizar_estados_guias_periodicamente() -> None:
    while True:
        with SessionLocal() as db:
            GuiaRepository(db).actualizar_guias_pendientes_vencidas()

        await asyncio.sleep(24 * 60 * 60)


@asynccontextmanager
async def lifespan(_: FastAPI):
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
    lifespan=lifespan,
)
register_exception_handlers(app)
app.include_router(agencia_router)
app.include_router(producto_router)
app.include_router(guia_router)
app.include_router(liquidacion_router)
app.include_router(cobranza_router)
app.include_router(inventario_router)
app.include_router(reporte_router)
