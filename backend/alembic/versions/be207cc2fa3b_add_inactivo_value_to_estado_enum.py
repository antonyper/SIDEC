"""add inactivo value to estado enum

Revision ID: be207cc2fa3b
Revises: bb7815f5e997
Create Date: 2026-09-12 01:39:02.947366

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be207cc2fa3b'
down_revision: Union[str, Sequence[str], None] = 'bb7815f5e997'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE estado ADD VALUE IF NOT EXISTS 'INACTIVO'")


def downgrade() -> None:
    """Downgrade schema."""
    # PostgreSQL does not support removing values from an enum type.
    pass
