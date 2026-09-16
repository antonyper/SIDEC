from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.db.dependencies import get_db
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario_schema import LoginRequest, TokenResponse, UsuarioResponse
from app.services.usuario_service import UsuarioService

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)

@router.post(
    "/login",
    response_model=TokenResponse,
    description="Inicia sesión y obtiene un token de acceso.",
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    repository = UsuarioRepository(db)
    service = UsuarioService(repository)
    return service.login(data)

@router.get(
    "/me",
    response_model=UsuarioResponse,
    description="Obtiene los datos del usuario autenticado.",
)
def me(
    usuario: Usuario = Depends(get_current_user),
):
    return UsuarioResponse.model_validate(usuario)
