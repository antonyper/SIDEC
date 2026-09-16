from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums.tipo_movimiento_inventario import TipoMovimientoInventario
from app.models.base_model import BaseModel


class MovimientoInventario(BaseModel):
    __tablename__ = "movimientos_inventario"

    producto_id: Mapped[int] = mapped_column(
        ForeignKey("producto.id"),
        nullable=False,
    )
    tipo: Mapped[TipoMovimientoInventario] = mapped_column(
        Enum(TipoMovimientoInventario),
        nullable=False,
    )
    cantidad: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    fecha: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    observacion: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    detalle_guia_id: Mapped[int | None] = mapped_column(
        ForeignKey("detalle_guia.id"),
        nullable=True,
    )
    detalle_liquidacion_id: Mapped[int | None] = mapped_column(
        ForeignKey("detalle_liquidaciones.id"),
        nullable=True,
    )

    producto: Mapped["Producto"] = relationship(
        "Producto",
        back_populates="movimientos_inventario",
    )

    @property
    def editable(self) -> bool:
        return self.detalle_guia_id is None and self.detalle_liquidacion_id is None
