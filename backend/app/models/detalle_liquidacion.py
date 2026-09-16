from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


class DetalleLiquidacion(BaseModel):
    __tablename__ = "detalle_liquidaciones"

    liquidacion_id: Mapped[int] = mapped_column(
        ForeignKey("liquidaciones.id"),
        nullable=False
    )

    detalle_guia_id: Mapped[int] = mapped_column(
        ForeignKey("detalle_guia.id"),
        nullable=False
    )

    cantidad_vendida: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    cantidad_devuelta: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    liquidacion = relationship(
        "Liquidacion",
        back_populates="detalles"
    )

    detalle_guia = relationship(
        "DetalleGuia",
        back_populates="detalles_liquidacion"
    )

    @property
    def fecha_liquidacion(self):
        return self.liquidacion.fecha if self.liquidacion else None

    def __repr__(self) -> str:
        return (
            f"<DetalleLiquidacion("
            f"id={self.id}, "
            f"liquidacion_id={self.liquidacion_id}, "
            f"detalle_guia_id={self.detalle_guia_id}"
            f")>"
        )