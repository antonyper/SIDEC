from decimal import Decimal

from app.schemas.base_schema import BaseSchema
from datetime import datetime
from app.enums.estado import Estado

# ==========================
# Commands
# ==========================

class AgenciaCreate(BaseSchema):
    nombre: str
    propietario: str | None = None
    agente: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    ruta: str | None = None
    latitud: Decimal | None = None
    longitud: Decimal | None = None

class AgenciaUpdate(BaseSchema):
    nombre: str | None = None
    propietario: str | None = None
    agente: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    ruta: str | None = None
    latitud: Decimal | None = None
    longitud: Decimal | None = None

# ==========================
# Queries
# ==========================

class AgenciaResponse(BaseSchema):
    id: int
    codigo: str
    nombre: str
    propietario: str | None = None
    agente: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    ruta: str | None = None
    latitud: Decimal | None = None
    longitud: Decimal | None = None
    estado: Estado
    created_at: datetime
    updated_at: datetime

class AgenciaListResponse(BaseSchema):
    id: int
    codigo: str
    nombre: str
    propietario: str | None = None
    agente: str | None = None
    telefono: str | None = None
    ruta: str | None = None
    estado: Estado

