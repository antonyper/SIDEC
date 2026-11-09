"""eliminar datos demo cargados en bifrost

Revision ID: 12303139a0f6
Revises: 90745d90e4d0
Create Date: 2026-11-05 22:09:34.422727

Borra las liquidaciones/guías marcadas "Datos demo%" y los 6 productos/agencias del seed
demo original. Corrige el intento anterior: ahora también borra los movimientos de
inventario ligados directo al producto (no solo a sus guías), que era lo que rompía el
borrado por una FK. Productos/agencias se identifican por (id, nombre) exactos del seed
conocido, no solo por nombre ni solo por id, para no coincidir por accidente con datos
reales de otra base que reutilice esos mismos ids o esos mismos nombres.
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "12303139a0f6"
down_revision: str | Sequence[str] | None = "90745d90e4d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
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
        DELETE FROM movimientos_inventario
        WHERE producto_id IN (
            SELECT id FROM producto WHERE (id, nombre) IN (
                (1, 'El Comercio'), (2, 'Gestión'), (3, 'Perú21'),
                (4, 'Trome'), (5, 'Ojo'), (6, 'Somos')
            )
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
    conn.execute(sa.text("""
        DELETE FROM agencias WHERE (id, nombre) IN (
            (1, 'Agencia Miraflores'), (2, 'Agencia San Isidro'), (3, 'Agencia Surco'),
            (4, 'Agencia Los Olivos'), (5, 'Agencia San Juan de Lurigancho'), (6, 'Agencia Callao')
        )
    """))
    conn.execute(sa.text("""
        DELETE FROM producto WHERE (id, nombre) IN (
            (1, 'El Comercio'), (2, 'Gestión'), (3, 'Perú21'),
            (4, 'Trome'), (5, 'Ojo'), (6, 'Somos')
        )
    """))


def downgrade() -> None:
    """No reversible: es un borrado de datos, no un cambio de esquema."""
