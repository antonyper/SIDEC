"""add ruta latitud longitud to agencias

Revision ID: 31daa0074b78
Revises: 6e4b05abcfdb
Create Date: 2026-09-12 18:03:28.097654

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31daa0074b78'
down_revision: Union[str, Sequence[str], None] = '6e4b05abcfdb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("agencias", sa.Column("ruta", sa.String(length=150), nullable=True))
    op.add_column("agencias", sa.Column("latitud", sa.Numeric(precision=9, scale=6), nullable=True))
    op.add_column("agencias", sa.Column("longitud", sa.Numeric(precision=9, scale=6), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("agencias", "longitud")
    op.drop_column("agencias", "latitud")
    op.drop_column("agencias", "ruta")
