from app.schemas.base_schema import BaseSchema
from datetime import datetime
from app.enums.estado import Estado

# ==========================
# Commands
# ==========================

class ProductoCreate(BaseSchema):
    nombre: str
    categoria: str | None = None
    precio: float
    
class ProductoUpdate(BaseSchema):
    nombre: str | None = None
    categoria: str | None = None
    precio: float | None = None

# ==========================
# Commands
# ==========================

class ProductoResponse(BaseSchema):
    id: int
    codigo: str
    nombre: str
    categoria: str | None = None
    precio: float | None = None
    estado: Estado
    created_at: datetime
    updated_at: datetime

class ProductoListResponse(BaseSchema):
    id: int
    codigo: str
    nombre: str
    categoria: str | None = None
    precio: float | None = None
    estado: Estado

