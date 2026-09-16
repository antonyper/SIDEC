from decimal import Decimal

from sqlalchemy import Enum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.enums.estado import Estado
from app.models.base_model import BaseModel

class Agencia(BaseModel):
    __tablename__ = "agencias"

    codigo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True
    )
    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )
    agente: Mapped[str] = mapped_column(
        String(150),
        nullable=True
    )
    propietario: Mapped[str] = mapped_column(
        String(150),
        nullable=True
    )
    telefono: Mapped[str] = mapped_column(
        String(20),
        nullable=True
    )
    direccion: Mapped[str] = mapped_column(
        String(250),
        nullable=True
    )
    ruta: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )
    latitud: Mapped[Decimal | None] = mapped_column(
        Numeric(9, 6),
        nullable=True
    )
    longitud: Mapped[Decimal | None] = mapped_column(
        Numeric(9, 6),
        nullable=True
    )
    estado: Mapped[Estado] = mapped_column(
        Enum(Estado),
        nullable=False,
        default=Estado.ACTIVO
    )
    guias: Mapped[list["Guia"]] = relationship(
        back_populates="agencia"
    )
    def __repr__(self) -> str:
        return f"<Agencia(codigo={self.codigo}, nombre={self.nombre})>"