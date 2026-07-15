from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column
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
    estado: Mapped[Estado] = mapped_column(
        Enum(Estado), 
        nullable=False, 
        default=Estado.ACTIVO
    )
    def __repr__(self) -> str:
        return f"<Agencia(codigo={self.codigo}, nombre={self.nombre})>"