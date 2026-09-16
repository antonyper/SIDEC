"""rename estadoguia pendiente to en_venta

Revision ID: 0604b720a37d
Revises: be207cc2fa3b
Create Date: 2026-09-12 13:21:43.939643

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0604b720a37d'
down_revision: Union[str, Sequence[str], None] = 'be207cc2fa3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE estadoguia RENAME VALUE 'PENDIENTE' TO 'EN_VENTA'")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TYPE estadoguia RENAME VALUE 'EN_VENTA' TO 'PENDIENTE'")
