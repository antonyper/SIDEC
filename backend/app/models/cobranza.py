from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums.estado_cobranza import EstadoCobranza
from app.models.base_model import BaseModel


class Cobranza(BaseModel):
    __tablename__ = "cobranzas"

    liquidacion_id: Mapped[int] = mapped_column(
        ForeignKey("liquidaciones.id"),
        nullable=False,
        unique=True
    )

    monto: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    monto_pagado: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    monto_pendiente: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    estado: Mapped[EstadoCobranza] = mapped_column(
        SQLEnum(EstadoCobranza),
        default=EstadoCobranza.COBRADO,
        nullable=False
    )

    liquidacion = relationship(
        "Liquidacion",
        back_populates="cobranza"
    )

    @property
    def agencia_nombre(self) -> str | None:
        if self.liquidacion and self.liquidacion.guia and self.liquidacion.guia.agencia:
            return self.liquidacion.guia.agencia.nombre
        return None

    def __repr__(self) -> str:
        return (
            f"<Cobranza("
            f"id={self.id}, "
            f"liquidacion_id={self.liquidacion_id}, "
            f"monto={self.monto}, "
            f"monto_pagado={self.monto_pagado}, "
            f"monto_pendiente={self.monto_pendiente}, "
            f"estado={self.estado}"
            f")>"
        )