from datetime import datetime
from sqlalchemy import Column, DateTime, func
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column

class BaseModel(Base):
    """Clase base para todos los modelos de la base de datos."""
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        primary_key=True, 
        autoincrement=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )