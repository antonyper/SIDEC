from datetime import date
from sqlalchemy import Enum, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.enums.estado_guia import EstadoGuia
from app.models.base_model import BaseModel

class Guia(BaseModel):
    __tablename__ = "guia"

    numero_guia: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False
    )
    fecha: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )
    estado: Mapped[EstadoGuia] = mapped_column(
        Enum(EstadoGuia),
        nullable=False,
        default=EstadoGuia.EN_VENTA
    )
    agencia_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("agencias.id"),
        nullable=False
    )
    observacion: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    agencia: Mapped["Agencia"] = relationship(
        "Agencia", 
        back_populates="guias"
    )

    detalles: Mapped[list["DetalleGuia"]] = relationship(
        back_populates="guia",
        cascade="all, delete-orphan"
    )

    liquidaciones: Mapped[list["Liquidacion"]] = relationship(
        back_populates="guia",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Guia(numero_guia={self.numero_guia}, "
            f"fecha={self.fecha}, "
            f"estado={self.estado})>"
        )


