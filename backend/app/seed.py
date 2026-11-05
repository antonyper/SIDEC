"""Ejecuta el seed a mano: `python -m app.seed [--demo]`.

Crea el ADMIN inicial y el ADMIN de SIDEC_SEED_ADMIN_* si faltan y, con --demo (o
SIDEC_SEED_DEMO=true), carga datos demo en una base sin agencias. Idempotente.
"""
import argparse
import logging

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.bootstrap_service import crear_admin_inicial
from app.services.seed_service import cargar_datos_demo, crear_admin_seed


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
    parser = argparse.ArgumentParser(description="Seed de SIDEC")
    parser.add_argument("--demo", action="store_true", help="cargar datos demo si no hay agencias")
    args = parser.parse_args()

    with SessionLocal() as db:
        crear_admin_inicial(db)
        crear_admin_seed(db)
        if args.demo or settings.SIDEC_SEED_DEMO:
            if not cargar_datos_demo(db):
                logging.getLogger("app.seed").info("La base ya tiene agencias: no se cargan datos demo.")


if __name__ == "__main__":
    main()
