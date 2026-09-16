from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.repositories.guia_repository import GuiaRepository
from app.db.dependencies import get_db
from app.repositories.liquidacion_repository import LiquidacionRepository
from app.services.liquidacion_service import LiquidacionService
from app.repositories.cobranza_repository import CobranzaRepository
from app.schemas.liquidacion_schema import (
    LiquidacionCreate,
    LiquidacionUpdate,
    LiquidacionResponse,
    LiquidacionListResponse,
    GuiaParaLiquidarResponse,
)


router = APIRouter(
    prefix="/liquidaciones",
    tags=["Liquidaciones"],
    dependencies=[Depends(get_current_user)],
)


# ==========================
# Dependencies
# ==========================

def get_liquidacion_service(
    db: Session = Depends(get_db)
):
    repository = LiquidacionRepository(db)
    guia_repository = GuiaRepository(db)
    cobranza_repository = CobranzaRepository(db)

    return LiquidacionService(
        repository,
        guia_repository,
        cobranza_repository
    )
# ==========================
# GET - Listar liquidaciones
# ==========================

@router.get(
    "",
    response_model=list[LiquidacionListResponse]
)
def get_all(
    service: LiquidacionService = Depends(get_liquidacion_service)
):
    return service.get_all()


# ==========================
# GET - Guía para liquidar
# ==========================

@router.get(
    "/guia/{guia_id}",
    response_model=GuiaParaLiquidarResponse
)
def get_guia_para_liquidar(
    guia_id: int,
    service: LiquidacionService = Depends(get_liquidacion_service)
):
    try:
        return service.get_guia_para_liquidar(guia_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


# ==========================
# GET - Liquidaciones por guía
# ==========================

@router.get(
    "/por-guia/{guia_id}",
    response_model=list[LiquidacionResponse]
)
def get_by_guia(
    guia_id: int,
    service: LiquidacionService = Depends(get_liquidacion_service)
):
    return service.get_by_guia_id(guia_id)


# ==========================
# GET - Liquidación por ID
# ==========================

@router.get(
    "/{liquidacion_id}",
    response_model=LiquidacionResponse
)
def get_by_id(
    liquidacion_id: int,
    service: LiquidacionService = Depends(get_liquidacion_service)
):
    try:
        return service.get_by_id(liquidacion_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


# ==========================
# POST - Crear liquidación
# ==========================

@router.post(
    "",
    response_model=LiquidacionResponse,
    status_code=status.HTTP_201_CREATED
)
def create(
    liquidacion_data: LiquidacionCreate,
    service: LiquidacionService = Depends(get_liquidacion_service)
):
    try:
        return service.create(liquidacion_data)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


# ==========================
# PUT - Actualizar liquidación
# ==========================

@router.put(
    "/{liquidacion_id}",
    response_model=LiquidacionResponse
)
def update(
    liquidacion_id: int,
    liquidacion_data: LiquidacionUpdate,
    service: LiquidacionService = Depends(get_liquidacion_service)
):
    try:
        return service.update(
            liquidacion_id,
            liquidacion_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


# ==========================
# PATCH - Anular liquidación
# ==========================

@router.patch(
    "/{liquidacion_id}/anular",
    response_model=LiquidacionResponse
)
def anular(
    liquidacion_id: int,
    service: LiquidacionService = Depends(get_liquidacion_service)
):
    try:
        return service.anular(liquidacion_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )