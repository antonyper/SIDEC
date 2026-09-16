from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.db.dependencies import get_db
from app.repositories.agencia_repository import AgenciaRepository
from app.schemas.agencia_schema import AgenciaCreate, AgenciaResponse, AgenciaListResponse, AgenciaUpdate
from app.services.agencia_service import AgenciaService
from typing import Annotated
from app.enums.estado import Estado

router = APIRouter(
    prefix="/agencias",
    tags=["Agencias"],
    dependencies=[Depends(get_current_user)],
)

@router.post(
    "",
    response_model=AgenciaResponse,
    description="Crea una nueva agencia con los datos proporcionados.",
)
def create_agencia(
    data: AgenciaCreate,
    db: Session = Depends(get_db),
):
    repository = AgenciaRepository(db)
    service = AgenciaService(repository)
    return service.create(data)

@router.get(
    "",
    response_model=list[AgenciaListResponse],
    description="Obtiene todas las agencias registradas.",
)
def get_agencias(
    nombre: str | None = None,
    propietario: str | None = None,
    estado: Estado | None = None,
    db: Session = Depends(get_db),
):
    repository = AgenciaRepository(db)
    service = AgenciaService(repository)

    return service.get_all(
        nombre=nombre,
        propietario=propietario,
        estado=estado,
    )

@router.get(
    "/{agencia_id}",
    response_model=AgenciaResponse,
    description="Obtiene el detalle de una agencia por su identificador.",
)
def get_agencia(
    agencia_id: int,
    db: Session = Depends(get_db),
):
    repository = AgenciaRepository(db)
    service = AgenciaService(repository)

    return service.get_by_id(agencia_id)

@router.put(
    "/{agencia_id}",
    response_model=AgenciaResponse,
    description="Actualiza los datos de una agencia existente.",
)
def update_agencia(
    agencia_id: int,
    data: AgenciaUpdate,
    db: Session = Depends(get_db),
):
    repository = AgenciaRepository(db)
    service = AgenciaService(repository)
    return service.update(agencia_id, data)

@router.patch(
    "/{agencia_id}/dar-baja",
    response_model=AgenciaResponse,
    description="Da de baja a una agencia existente.",
)
def dar_baja_agencia(
    agencia_id: int,
    db: Session = Depends(get_db),
):
    repository = AgenciaRepository(db)
    service = AgenciaService(repository)
    return service.dar_baja(agencia_id)

@router.patch(
    "/{agencia_id}/reactivar",
    response_model=AgenciaResponse,
    description="Reactiva una agencia que estaba dada de baja.",
)
def reactivar_agencia(
    agencia_id: int,
    db: Session = Depends(get_db),
):
    repository = AgenciaRepository(db)
    service = AgenciaService(repository)
    return service.reactivar(agencia_id)
