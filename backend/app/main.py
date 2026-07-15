from fastapi import FastAPI

from app.api.v1.agencia_router import router as agencia_router
from app.core.config import settings
from app.core.exception_handler import register_exception_handlers

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)
register_exception_handlers(app)
app.include_router(agencia_router)
