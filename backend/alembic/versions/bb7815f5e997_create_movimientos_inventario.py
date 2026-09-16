"""create movimientos_inventario

Revision ID: bb7815f5e997
Revises: 8ba7f3cb214d
Create Date: 2026-09-12 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "bb7815f5e997"
down_revision: Union[str, Sequence[str], None] = "8ba7f3cb214d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "movimientos_inventario",
        sa.Column("producto_id", sa.Integer(), nullable=False),
        sa.Column(
            "tipo",
            sa.Enum(
                "STOCK_INICIAL",
                "INGRESO",
                "SALIDA_GUIA",
                "DEVOLUCION",
                name="tipomovimientoinventario",
            ),
            nullable=False,
        ),
        sa.Column("cantidad", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("observacion", sa.String(length=500), nullable=True),
        sa.Column("detalle_guia_id", sa.Integer(), nullable=True),
        sa.Column("detalle_liquidacion_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("cantidad > 0", name="ck_movimiento_inventario_cantidad_positiva"),
        sa.ForeignKeyConstraint(["producto_id"], ["producto.id"]),
        sa.ForeignKeyConstraint(["detalle_guia_id"], ["detalle_guia.id"]),
        sa.ForeignKeyConstraint(
            ["detalle_liquidacion_id"],
            ["detalle_liquidaciones.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("detalle_guia_id"),
        sa.UniqueConstraint("detalle_liquidacion_id"),
    )


def downgrade() -> None:
    op.drop_table("movimientos_inventario")
    sa.Enum(name="tipomovimientoinventario").drop(op.get_bind(), checkfirst=True)
