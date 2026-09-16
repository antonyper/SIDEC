from datetime import date
from decimal import Decimal

from app.schemas.base_schema import BaseSchema

# ==========================
# Commands
# ==========================

class DetalleGuiaCreate(BaseSchema):
    producto_id: int
    cantidad: int
    precio: Decimal | None = None
    porcentaje_cobro: Decimal | None = None

# ==========================
# Queries
# ==========================

class DetalleLiquidacionInfo(BaseSchema):
    liquidacion_id: int
    cantidad_vendida: int
    fecha_liquidacion: date

class DetalleGuiaResponse(BaseSchema):
    id: int
    producto_id: int
    cantidad: int
    precio: Decimal | None = None
    porcentaje_cobro: Decimal | None = None
    liquidaciones_activas: list[DetalleLiquidacionInfo] = []

class DetalleGuiaUpdate(BaseSchema):
    detalle_guia_id: int | None = None
    producto_id: int
    cantidad: int
    precio: Decimal | None = None
    porcentaje_cobro: Decimal | None = None