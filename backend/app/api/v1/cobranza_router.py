from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


from app.db.dependencies import get_db
from app.repositories.cobranza_repository import CobranzaRepository
from app.schemas.cobranza_schema import (
    CobranzaResponse,
    CobranzaUpdate
)
from app.services.cobranza_service import CobranzaService


router = APIRouter(
    prefix="/cobranzas",
    tags=["Cobranzas"]
)


def get_cobranza_service(
    db: Session = Depends(get_db)
):
    repository = CobranzaRepository(db)

    return CobranzaService(repository)


@router.get(
    "",
    response_model=list[CobranzaResponse]
)
def get_all(
    service: CobranzaService = Depends(
        get_cobranza_service
    )
):
    return service.get_all()


@router.get(
    "/liquidacion/{liquidacion_id}",
    response_model=CobranzaResponse
)
def get_by_liquidacion_id(
    liquidacion_id: int,
    service: CobranzaService = Depends(
        get_cobranza_service
    )
):
    try:
        return service.get_by_liquidacion_id(
            liquidacion_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "/{cobranza_id}",
    response_model=CobranzaResponse
)
def get_by_id(
    cobranza_id: int,
    service: CobranzaService = Depends(
        get_cobranza_service
    )
):
    try:
        return service.get_by_id(cobranza_id)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.put(
    "/{cobranza_id}",
    response_model=CobranzaResponse
)
def update(
    cobranza_id: int,
    cobranza_data: CobranzaUpdate,
    service: CobranzaService = Depends(
        get_cobranza_service
    )
):
    try:
        return service.update(
            cobranza_id,
            cobranza_data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )