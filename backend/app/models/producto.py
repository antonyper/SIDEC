from sqlalchemy import Boolean, Enum, String, Integer, Numeric, DateTime
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.enums.estado import Estado
from app.models.base_model import BaseModel
from app.db.base import Base

class Producto(Base):
    __tablename__ = "producto"

    id = mapped_column(Integer, primary_key=True)
    codigo = mapped_column(String(10), unique=True, nullable=False)
    nombre = mapped_column(String(100), nullable=False)
    categoria = mapped_column(String(50), nullable=True)
    precio = mapped_column(Numeric(10, 2), nullable=False)
    estado = mapped_column(
        Enum(Estado),
        default=Estado.ACTIVO,
        nullable=False
    )
    eliminado = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    created_at = mapped_column(
        DateTime(timezone=True), 
        default=datetime.now)
    updated_at = mapped_column(
        DateTime(timezone=True),
        default=datetime.now,
        onupdate=datetime.now
    )
    detalles_guia: Mapped[list["DetalleGuia"]] = relationship(
        back_populates="producto",
    )
    movimientos_inventario: Mapped[list["MovimientoInventario"]] = relationship(
        "MovimientoInventario",
        back_populates="producto",
    )

    def __repr__(self):
        return f"<Producto {self.codigo} - {self.nombre}>"
