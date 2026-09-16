from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column
from app.enums.rol_usuario import RolUsuario
from app.models.base_model import BaseModel


class Usuario(BaseModel):
    __tablename__ = "usuarios"

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    rol: Mapped[RolUsuario] = mapped_column(
        Enum(RolUsuario),
        nullable=False,
        default=RolUsuario.OPERADOR
    )
    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    def __repr__(self) -> str:
        return f"<Usuario(username={self.username}, rol={self.rol})>"
