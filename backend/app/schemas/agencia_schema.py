from app.schemas.base_schema import BaseSchema
from datetime import datetime
from app.enums.estado import Estado

class AgenciaCreate(BaseSchema):
    nombre: str
    propietario: str | None = None
    agente: str | None = None
    telefono: str | None = None
    direccion: str | None = None

class AgenciaResponse(BaseSchema):
    id: int
    codigo: str
    nombre: str
    propietario: str | None = None
    agente: str | None = None
    telefono: str | None = None
    direccion: str | None = None
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
    estado: Estado

class AgenciaUpdate(BaseSchema):
    nombre: str | None = None
    propietario: str | None = None
    agente: str | None = None
    telefono: str | None = None
    direccion: str | None = None
