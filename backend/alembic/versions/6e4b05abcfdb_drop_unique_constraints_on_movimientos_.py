"""drop unique constraints on movimientos_inventario fk columns

Revision ID: 6e4b05abcfdb
Revises: 4968dc4e7608
Create Date: 2026-09-12 14:56:29.855331

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e4b05abcfdb'
down_revision: Union[str, Sequence[str], None] = '4968dc4e7608'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        "movimientos_inventario_detalle_guia_id_key",
        "movimientos_inventario",
        type_="unique",
    )
    op.drop_constraint(
        "movimientos_inventario_detalle_liquidacion_id_key",
        "movimientos_inventario",
        type_="unique",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.create_unique_constraint(
        "movimientos_inventario_detalle_liquidacion_id_key",
        "movimientos_inventario",
        ["detalle_liquidacion_id"],
    )
    op.create_unique_constraint(
        "movimientos_inventario_detalle_guia_id_key",
        "movimientos_inventario",
        ["detalle_guia_id"],
    )
