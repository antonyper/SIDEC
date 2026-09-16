from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel

class DetalleGuia(BaseModel):
    __tablename__ = "detalle_guia"

    guia_id: Mapped[int] = mapped_column(
        ForeignKey("guia.id"), 
        nullable=False
    )
    producto_id: Mapped[int] = mapped_column(
        ForeignKey("producto.id"), 
        nullable=False
    )
    cantidad: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), 
        nullable=False
    )
    precio: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), 
        nullable=False
    )
    porcentaje_cobro: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False
    )
    
    guia = relationship(
        "Guia", 
        back_populates="detalles"
    )

    producto = relationship(
        "Producto",
        back_populates="detalles_guia")
    
    detalles_liquidacion: Mapped[list["DetalleLiquidacion"]] = relationship(
        back_populates="detalle_guia",
        cascade="all, delete-orphan"
    )

    @property
    def liquidaciones_activas(self) -> list["DetalleLiquidacion"]:
        from app.enums.estado_liquidacion import EstadoLiquidacion

        return [
            detalle_liquidacion
            for detalle_liquidacion in self.detalles_liquidacion
            if detalle_liquidacion.liquidacion.estado == EstadoLiquidacion.LIQUIDADO
        ]

    def __repr__(self) -> str:
        return (
            f"<DetalleGuia(guia_id={self.guia_id}, "
            f"producto_id={self.producto_id}, "
            f"cantidad={self.cantidad}, "
            f"precio={self.precio}, "
            f"porcentaje_cobro={self.porcentaje_cobro})>"
        )