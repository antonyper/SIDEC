"""La revisión de limpieza no debe bloquear el arranque ni borrar datos."""
import importlib.util
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.script import ScriptDirectory

BACKEND = Path(__file__).resolve().parents[1]


@pytest.fixture
def migration():
    path = next((BACKEND / "alembic/versions").glob("12303139a0f6_*.py"))
    spec = importlib.util.spec_from_file_location("cleanup_revision", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("populated", [False, True])
def test_upgrade_preserves_inventory_and_matching_names(migration, populated):
    engine = sa.create_engine("sqlite://")
    with engine.begin() as conn:
        conn.exec_driver_sql("PRAGMA foreign_keys=ON")
        # Reproduce las referencias que impedían borrar los productos del seed.
        conn.exec_driver_sql("CREATE TABLE producto (id INTEGER PRIMARY KEY, nombre TEXT)")
        conn.exec_driver_sql("CREATE TABLE agencias (id INTEGER PRIMARY KEY, nombre TEXT)")
        conn.exec_driver_sql(
            "CREATE TABLE guia (id INTEGER PRIMARY KEY, observacion TEXT)"
        )
        conn.exec_driver_sql(
            "CREATE TABLE detalle_guia (id INTEGER PRIMARY KEY, guia_id INTEGER)"
        )
        conn.exec_driver_sql(
            "CREATE TABLE liquidaciones (id INTEGER PRIMARY KEY, observacion TEXT)"
        )
        conn.exec_driver_sql(
            "CREATE TABLE detalle_liquidaciones "
            "(id INTEGER PRIMARY KEY, liquidacion_id INTEGER)"
        )
        conn.exec_driver_sql(
            "CREATE TABLE cobranzas (id INTEGER PRIMARY KEY, liquidacion_id INTEGER)"
        )
        conn.exec_driver_sql(
            "CREATE TABLE movimientos_inventario "
            "(id INTEGER PRIMARY KEY, producto_id INTEGER REFERENCES producto(id), "
            "detalle_guia_id INTEGER, detalle_liquidacion_id INTEGER)"
        )
        if populated:
            conn.exec_driver_sql(
                "INSERT INTO producto VALUES (1, 'El Comercio'), (2, 'Producto real')"
            )
            conn.exec_driver_sql("INSERT INTO agencias VALUES (1, 'Agencia Miraflores')")
            conn.exec_driver_sql(
                "INSERT INTO movimientos_inventario VALUES (1, 1, NULL, NULL)"
            )
        tables = ("producto", "agencias", "movimientos_inventario")

        def snapshot():
            return {
                table: conn.exec_driver_sql(f"SELECT * FROM {table} ORDER BY id").all()
                for table in tables
            }

        before = snapshot()
        with Operations.context(MigrationContext.configure(conn)):
            migration.upgrade()
            migration.upgrade()  # Reintentar tampoco debe modificar datos.
            migration.downgrade()
        assert snapshot() == before
    engine.dispose()


def test_revision_remains_single_head(migration):
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND / "alembic"))
    scripts = ScriptDirectory.from_config(config)
    assert scripts.get_heads() == [migration.revision]
    assert scripts.get_revision(migration.revision).down_revision == "90745d90e4d0"
