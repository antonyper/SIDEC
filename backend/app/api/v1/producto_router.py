from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.repositories.producto_repository import ProductoRepository
from app.schemas.producto_schema import ProductoCreate, ProductoResponse, ProductoListResponse, ProductoUpdate
from app.services.producto_service import ProductoService
from typing import Annotated
from app.enums.estado import Estado

router = APIRouter(
    prefix="/productos",
    tags=["Productos"],
)

@router.post(
    "",
    response_model=ProductoResponse,
    description="Crea un nuevo producto con los datos proporcionados.",
)
def create_producto(
    data: ProductoCreate,
    db: Session = Depends(get_db),
):
    repository = ProductoRepository(db)
    service = ProductoService(repository)
    return service.create(data)

@router.get(
    "",
    response_model=list[ProductoListResponse],
    description="Obtiene todos los productos registrados.",
)
def get_productos(
    nombre: str | None = None,
    categoria: str | None = None,
    estado: Estado | None = None,
    precio: float | None = None,
    buscar: str | None = None,
    db: Session = Depends(get_db),
):
    repository = ProductoRepository(db)
    service = ProductoService(repository)

    return service.get_all(
        nombre=nombre,
        categoria=categoria,
        estado=estado,
        precio=precio,
        buscar=buscar,
    )

@router.get(
    "/{producto_id}",
    response_model=ProductoResponse,
    description="Obtiene el detalle de un producto por su identificador.",
)
def get_producto(
    producto_id: int,
    db: Session = Depends(get_db),
):
    repository = ProductoRepository(db)
    service = ProductoService(repository)

    return service.get_by_id(producto_id)

@router.put(
    "/{producto_id}",
    response_model=ProductoResponse,
    description="Actualiza los datos de un producto existente.",
)
def update_producto(
    producto_id: int,
    data: ProductoUpdate,
    db: Session = Depends(get_db),
):
    repository = ProductoRepository(db)
    service = ProductoService(repository)
    return service.update(producto_id, data)

@router.patch(
    "/{producto_id}/dar-baja",
    response_model=ProductoResponse,
    description="Da de baja a un producto existente.",
)
def dar_baja_producto(
    producto_id: int,
    db: Session = Depends(get_db),
):
    repository = ProductoRepository(db)
    service = ProductoService(repository)
    return service.dar_baja(producto_id)

@router.patch(
    "/{producto_id}/reactivar",
    response_model=ProductoResponse,
    description="Reactiva un producto que estaba dada de baja.",
)
def reactivar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
):
    repository = ProductoRepository(db)
    service = ProductoService(repository)
    return service.reactivar(producto_id)

@router.delete(
    "/{producto_id}",
    description="Elimina un producto (soft delete): deja de verse en la web pero se conserva en la base de datos.",
)
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
):
    repository = ProductoRepository(db)
    service = ProductoService(repository)
    service.eliminar(producto_id)
    return {"message": "Producto eliminado correctamente."}
