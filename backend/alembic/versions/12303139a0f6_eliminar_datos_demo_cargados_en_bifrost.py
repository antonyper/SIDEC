"""eliminar datos demo cargados en bifrost

Revision ID: 12303139a0f6
Revises: 90745d90e4d0
Create Date: 2026-11-05 22:09:34.422727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12303139a0f6'
down_revision: Union[str, Sequence[str], None] = '90745d90e4d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


AGENCIAS_DEMO = (
    "Agencia Miraflores", "Agencia San Isidro", "Agencia Surco",
    "Agencia Los Olivos", "Agencia San Juan de Lurigancho", "Agencia Callao",
)
PRODUCTOS_DEMO = ("El Comercio", "Gestión", "Perú21", "Trome", "Ojo", "Somos")


def upgrade() -> None:
    """Borra los datos demo (liquidaciones/guías marcadas 'Datos demo%' y sus agencias/
    productos) cargados al desplegar Bifrost. Filtra por marcadores estables, no por id:
    re-ejecutar esta migración cuando ya no quede nada que coincida es un no-op seguro."""
    conn = op.get_bind()

    conn.execute(sa.text("""
        DELETE FROM movimientos_inventario
        WHERE detalle_liquidacion_id IN (
            SELECT dl.id FROM detalle_liquidaciones dl
            JOIN liquidaciones l ON l.id = dl.liquidacion_id
            WHERE l.observacion LIKE 'Datos demo%'
        )
    """))
    conn.execute(sa.text("""
        DELETE FROM movimientos_inventario
        WHERE detalle_guia_id IN (
            SELECT dg.id FROM detalle_guia dg
            JOIN guia g ON g.id = dg.guia_id
            WHERE g.observacion LIKE 'Datos demo%'
        )
    """))
    conn.execute(sa.text("""
        DELETE FROM cobranzas
        WHERE liquidacion_id IN (SELECT id FROM liquidaciones WHERE observacion LIKE 'Datos demo%')
    """))
    conn.execute(sa.text("""
        DELETE FROM detalle_liquidaciones
        WHERE liquidacion_id IN (SELECT id FROM liquidaciones WHERE observacion LIKE 'Datos demo%')
    """))
    conn.execute(sa.text("DELETE FROM liquidaciones WHERE observacion LIKE 'Datos demo%'"))
    conn.execute(sa.text("""
        DELETE FROM detalle_guia
        WHERE guia_id IN (SELECT id FROM guia WHERE observacion LIKE 'Datos demo%')
    """))
    conn.execute(sa.text("DELETE FROM guia WHERE observacion LIKE 'Datos demo%'"))
    conn.execute(
        sa.text("DELETE FROM agencias WHERE nombre IN :nombres").bindparams(
            sa.bindparam("nombres", expanding=True)
        ),
        {"nombres": list(AGENCIAS_DEMO)},
    )
    conn.execute(
        sa.text("DELETE FROM producto WHERE nombre IN :nombres").bindparams(
            sa.bindparam("nombres", expanding=True)
        ),
        {"nombres": list(PRODUCTOS_DEMO)},
    )


def downgrade() -> None:
    """No reversible: es un borrado de datos, no un cambio de esquema."""
    pass
