"""Retirar la limpieza automática de datos demo del arranque.

Revision ID: 12303139a0f6
Revises: 90745d90e4d0
Create Date: 2026-11-05 22:09:34.422727

Esta revisión conserva su identidad para bases que ya la hayan aplicado. La limpieza
original fallaba por referencias de inventario y podía seleccionar datos reales por
nombre. Las migraciones de arranque no deben borrar esos datos; cualquier limpieza
de producción corresponde a Jack Torpoco, manualmente.
"""
from collections.abc import Sequence

revision: str = "12303139a0f6"
down_revision: str | Sequence[str] | None = "90745d90e4d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Conserva los datos existentes y permite completar el arranque."""


def downgrade() -> None:
    """No hay cambios de esquema ni de datos que revertir."""
