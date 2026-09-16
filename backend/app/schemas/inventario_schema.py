from datetime import date
from decimal import Decimal

from app.enums.tipo_movimiento_inventario import TipoMovimientoInventario
from app.schemas.base_schema import BaseSchema


class MovimientoInventarioCreate(BaseSchema):
    producto_id: int
    tipo: TipoMovimientoInventario
    cantidad: Decimal
    fecha: date
    observacion: str | None = None


class InventarioItemResponse(BaseSchema):
    producto_id: int
    codigo: str
    producto: str
    stock: Decimal


class MovimientoInventarioUpdate(BaseSchema):
    tipo: TipoMovimientoInventario
    cantidad: Decimal
    fecha: date
    observacion: str | None = None


class MovimientoInventarioResponse(BaseSchema):
    id: int
    tipo: TipoMovimientoInventario
    cantidad: Decimal
    fecha: date
    observacion: str | None = None
    editable: bool
