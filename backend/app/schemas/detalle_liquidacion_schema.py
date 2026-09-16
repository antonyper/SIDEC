from decimal import Decimal

from app.schemas.base_schema import BaseSchema

# ========================
# Commands
# ========================

class DetalleLiquidacionCreate(BaseSchema):
    detalle_guia_id: int
    cantidad_devuelta: int
    precio_a_liquidar: Decimal | None = None

class DetalleLiquidacionUpdate(BaseSchema):
    detalle_guia_id: int
    cantidad_devuelta: int | None = None
    precio_a_liquidar: Decimal | None = None

# ========================
# Queries
# ========================

class DetalleLiquidacionResponse(BaseSchema):
    id: int
    detalle_guia_id: int
    cantidad_vendida: int
    cantidad_devuelta: int
    total: Decimal