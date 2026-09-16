from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.db.dependencies import get_db
from app.repositories.guia_repository import GuiaRepository
from app.schemas.guia_schema import (
    GuiaCreate,
    GuiaResponse,
    GuiaListResponse,
    GuiaUpdate,
)
from app.services.guia_service import GuiaService

router = APIRouter(
    prefix="/guias",
    tags=["Guías"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[GuiaListResponse])
def get_guias(db: Session = Depends(get_db)):
    repository = GuiaRepository(db)
    service = GuiaService(repository)

    return service.get_all()


@router.get("/{guia_id}", response_model=GuiaResponse)
def get_guia(guia_id: int, db: Session = Depends(get_db)):
    repository = GuiaRepository(db)
    service = GuiaService(repository)

    try:
        return service.get_by_id(guia_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", response_model=GuiaResponse, status_code=201)
def create_guia(
    guia: GuiaCreate,
    db: Session = Depends(get_db)
):
    repository = GuiaRepository(db)
    service = GuiaService(repository)

    try:
        return service.create(guia)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{guia_id}", response_model=GuiaResponse)
def update_guia(
    guia_id: int,
    guia: GuiaUpdate,
    db: Session = Depends(get_db)
):
    repository = GuiaRepository(db)
    service = GuiaService(repository)

    try:
        return service.update(guia_id, guia)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{guia_id}")
def delete_guia(
    guia_id: int,
    db: Session = Depends(get_db)
):
    repository = GuiaRepository(db)
    service = GuiaService(repository)

    try:
        service.delete(guia_id)
        return {"message": "Guía anulada correctamente."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))