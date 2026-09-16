from datetime import date, datetime
from decimal import Decimal

from app.enums.estado_liquidacion import EstadoLiquidacion
from app.schemas.base_schema import BaseSchema
from app.schemas.detalle_liquidacion_schema import (
    DetalleLiquidacionCreate,
    DetalleLiquidacionResponse,
    DetalleLiquidacionUpdate,
)

# ========================
# Commands
# ========================

class LiquidacionCreate(BaseSchema):
    fecha: date
    guia_id: int
    observacion: str | None = None
    detalles: list[DetalleLiquidacionCreate] | None = None
    pago_a_cuenta: Decimal = Decimal("0.00")

class LiquidacionUpdate(BaseSchema):
    fecha: date | None = None
    observacion: str | None = None
    detalles: list[DetalleLiquidacionUpdate] | None = None

# ========================
# Queries
# ========================

class LiquidacionResponse(BaseSchema):
    id: int
    fecha: date
    guia_id: int
    estado: EstadoLiquidacion
    observacion: str | None = None
    detalles: list[DetalleLiquidacionResponse]
    created_at: datetime
    updated_at: datetime


class LiquidacionListResponse(BaseSchema):
    id: int
    fecha: date
    guia_id: int
    estado: EstadoLiquidacion
    observacion: str | None = None

# ==========================
# Guía para liquidar
# ==========================


class DetalleGuiaParaLiquidarResponse(BaseSchema):
    detalle_guia_id: int
    producto_id: int
    producto: str
    cantidad: int
    precio: Decimal
    porcentaje_cobro: Decimal
    precio_a_liquidar: Decimal


class GuiaParaLiquidarResponse(BaseSchema):
    guia_id: int
    numero_guia: str
    fecha: date
    agencia_id: int
    agencia: str
    detalles: list[DetalleGuiaParaLiquidarResponse]

# ==========================
# Rebuild Pydantic
# ==========================

GuiaParaLiquidarResponse.model_rebuild()