from decimal import Decimal

from app.enums.estado_cobranza import EstadoCobranza
from app.schemas.base_schema import BaseSchema


class CobranzaUpdate(BaseSchema):
    monto_pagado: Decimal


class CobranzaResponse(BaseSchema):
    id: int
    liquidacion_id: int
    agencia_nombre: str | None = None
    monto: Decimal
    monto_pagado: Decimal
    monto_pendiente: Decimal
    estado: EstadoCobranza