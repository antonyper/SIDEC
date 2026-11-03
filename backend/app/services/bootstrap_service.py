import logging

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.enums.rol_usuario import RolUsuario
from app.models.usuario import Usuario

logger = logging.getLogger(__name__)


def crear_admin_inicial(db: Session) -> bool:
    """Crea el primer ADMIN si no existe ningún usuario.

    Sin esto, una base nueva no tiene a nadie que pueda iniciar sesión: no hay
    registro público y solo un ADMIN puede crear cuentas. Nunca toca una base que
    ya tiene usuarios, así que no sirve para resetear contraseñas.
    """
    if db.scalar(select(func.count()).select_from(Usuario)):
        return False

    if not settings.SIDEC_ADMIN_USERNAME or not settings.SIDEC_ADMIN_PASSWORD:
        logger.warning(
            "No hay usuarios y faltan SIDEC_ADMIN_USERNAME/SIDEC_ADMIN_PASSWORD: "
            "nadie podrá iniciar sesión hasta crear el primer ADMIN."
        )
        return False

    db.add(
        Usuario(
            nombre=settings.SIDEC_ADMIN_NOMBRE,
            username=settings.SIDEC_ADMIN_USERNAME,
            password_hash=hash_password(settings.SIDEC_ADMIN_PASSWORD),
            rol=RolUsuario.ADMIN,
        )
    )
    try:
        db.commit()
    except IntegrityError:
        # Otra réplica lo creó a la vez: el resultado es el mismo.
        db.rollback()
        return False

    logger.info("ADMIN inicial '%s' creado.", settings.SIDEC_ADMIN_USERNAME)
    return True
