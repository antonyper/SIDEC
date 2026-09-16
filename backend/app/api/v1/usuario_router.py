from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth_dependencies import require_admin
from app.db.dependencies import get_db
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario_schema import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.services.usuario_service import UsuarioService

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
    dependencies=[Depends(require_admin)],
)

@router.post(
    "",
    response_model=UsuarioResponse,
    description="Crea un nuevo usuario con acceso al sistema.",
)
def create_usuario(
    data: UsuarioCreate,
    db: Session = Depends(get_db),
):
    repository = UsuarioRepository(db)
    service = UsuarioService(repository)
    return service.create(data)

@router.get(
    "",
    response_model=list[UsuarioResponse],
    description="Obtiene todos los usuarios registrados.",
)
def get_usuarios(
    db: Session = Depends(get_db),
):
    repository = UsuarioRepository(db)
    service = UsuarioService(repository)
    return service.get_all()

@router.put(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    description="Actualiza los datos de un usuario existente.",
)
def update_usuario(
    usuario_id: int,
    data: UsuarioUpdate,
    db: Session = Depends(get_db),
):
    repository = UsuarioRepository(db)
    service = UsuarioService(repository)
    return service.update(usuario_id, data)

@router.patch(
    "/{usuario_id}/dar-baja",
    response_model=UsuarioResponse,
    description="Desactiva el acceso de un usuario.",
)
def dar_baja_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
):
    repository = UsuarioRepository(db)
    service = UsuarioService(repository)
    return service.dar_baja(usuario_id)

@router.patch(
    "/{usuario_id}/reactivar",
    response_model=UsuarioResponse,
    description="Reactiva el acceso de un usuario.",
)
def reactivar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
):
    repository = UsuarioRepository(db)
    service = UsuarioService(repository)
    return service.reactivar(usuario_id)
