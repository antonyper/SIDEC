"""add eliminado (soft delete) to producto

Revision ID: 712b911caf48
Revises: 31daa0074b78
Create Date: 2026-09-15 20:43:15.866942

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '712b911caf48'
down_revision: Union[str, Sequence[str], None] = '31daa0074b78'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "producto",
        sa.Column("eliminado", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("producto", "eliminado")
