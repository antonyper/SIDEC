from datetime import date, datetime

from app.enums.estado_guia import EstadoGuia
from app.schemas.base_schema import BaseSchema
from app.schemas.detalle_guia_schema import DetalleGuiaCreate, DetalleGuiaResponse, DetalleGuiaUpdate

# =========================
# Commands
# =========================

class GuiaCreate(BaseSchema):
    fecha: date
    agencia_id: int
    observacion: str | None = None
    detalles: list[DetalleGuiaCreate] | None = None

class GuiaUpdate(BaseSchema):
    fecha: date | None = None
    estado: EstadoGuia | None = None
    observacion: str | None = None
    detalles: list[DetalleGuiaUpdate] | None = None

class GuiaResponse(BaseSchema):
    id: int
    numero_guia: str
    fecha: date
    agencia_id: int
    estado: EstadoGuia
    observacion: str | None

    detalles: list[DetalleGuiaResponse]


class GuiaListResponse(BaseSchema):
    id: int
    numero_guia: str
    fecha: date
    agencia_id: int
    estado: EstadoGuia
    observacion: str | None

    detalles: list[DetalleGuiaResponse]