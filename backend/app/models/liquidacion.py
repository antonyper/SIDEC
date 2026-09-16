from datetime import date

from sqlalchemy import Date, Enum as SQLEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.enums.estado_liquidacion import EstadoLiquidacion


class Liquidacion(BaseModel):
    __tablename__ = "liquidaciones"

    fecha: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    guia_id: Mapped[int] = mapped_column(
        ForeignKey("guia.id"),
        nullable=False
    )

    estado: Mapped[EstadoLiquidacion] = mapped_column(
        SQLEnum(EstadoLiquidacion),
        default=EstadoLiquidacion.LIQUIDADO,
        nullable=False
    )

    observacion: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    guia = relationship(
        "Guia",
        back_populates="liquidaciones"
    )

    detalles = relationship(
        "DetalleLiquidacion",
        back_populates="liquidacion"
    )

    cobranza = relationship(
        "Cobranza",
        back_populates="liquidacion",
        uselist=False
    )  

    def __repr__(self) -> str:
        return (
            f"<Liquidacion("
            f"id={self.id}, "
            f"guia_id={self.guia_id}, "
            f"estado={self.estado}"
            f")>"
        )