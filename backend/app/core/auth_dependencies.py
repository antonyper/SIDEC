import jwt
from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.dependencies import get_db
from app.domain.exceptions.base_exception import BusinessException
from app.domain.exceptions.usuario_exception import NoAutenticadoException, UsuarioInactivoException
from app.enums.rol_usuario import RolUsuario
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    if credentials is None:
        raise NoAutenticadoException()
    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise NoAutenticadoException() from exc

    usuario = UsuarioRepository(db).get_by_id(int(payload["sub"]))
    if not usuario:
        raise NoAutenticadoException()
    if not usuario.activo:
        raise UsuarioInactivoException()
    return usuario


def require_admin(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    if usuario.rol != RolUsuario.ADMIN:
        raise BusinessException("No tienes permisos para realizar esta acción.", status_code=status.HTTP_403_FORBIDDEN)
    return usuario
