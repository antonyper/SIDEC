"""rename estadoliquidacion activa to liquidado

Revision ID: 4968dc4e7608
Revises: 0604b720a37d
Create Date: 2026-09-12 14:19:25.977509

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4968dc4e7608'
down_revision: Union[str, Sequence[str], None] = '0604b720a37d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE estadoliquidacion RENAME VALUE 'ACTIVA' TO 'LIQUIDADO'")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TYPE estadoliquidacion RENAME VALUE 'LIQUIDADO' TO 'ACTIVA'")
