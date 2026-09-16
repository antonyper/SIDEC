from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.enums.tipo_movimiento_inventario import TipoMovimientoInventario
from app.models.movimiento_inventario import MovimientoInventario
from app.models.producto import Producto
from app.schemas.inventario_schema import (
    InventarioItemResponse,
    MovimientoInventarioCreate,
    MovimientoInventarioResponse,
    MovimientoInventarioUpdate,
)

router = APIRouter(prefix="/inventario", tags=["Inventario"])


@router.get("", response_model=list[InventarioItemResponse])
def get_inventario(db: Session = Depends(get_db)):
    entradas = case(
        (
            MovimientoInventario.tipo.in_(
                [
                    TipoMovimientoInventario.STOCK_INICIAL,
                    TipoMovimientoInventario.INGRESO,
                    TipoMovimientoInventario.DEVOLUCION,
                ]
            ),
            MovimientoInventario.cantidad,
        ),
        else_=-MovimientoInventario.cantidad,
    )
    return db.execute(
        select(
            Producto.id.label("producto_id"),
            Producto.codigo,
            Producto.nombre.label("producto"),
            func.coalesce(func.sum(entradas), 0).label("stock"),
        )
        .outerjoin(MovimientoInventario)
        .group_by(Producto.id, Producto.codigo, Producto.nombre)
        .order_by(Producto.nombre)
    ).mappings().all()


@router.get("/{producto_id}/movimientos", response_model=list[MovimientoInventarioResponse])
def get_movimientos_por_producto(producto_id: int, db: Session = Depends(get_db)):
    if not db.get(Producto, producto_id):
        raise HTTPException(status_code=404, detail="El producto no existe.")

    return db.scalars(
        select(MovimientoInventario)
        .where(MovimientoInventario.producto_id == producto_id)
        .order_by(MovimientoInventario.fecha.desc(), MovimientoInventario.id.desc())
    ).all()


@router.post("/movimientos", status_code=status.HTTP_201_CREATED)
def create_movimiento(
    movimiento: MovimientoInventarioCreate,
    db: Session = Depends(get_db),
):
    if movimiento.tipo not in (
        TipoMovimientoInventario.STOCK_INICIAL,
        TipoMovimientoInventario.INGRESO,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden registrar manualmente stock inicial o ingresos.",
        )
    if movimiento.cantidad <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cantidad debe ser mayor que cero.",
        )
    if not db.get(Producto, movimiento.producto_id):
        raise HTTPException(status_code=404, detail="El producto no existe.")

    registro = MovimientoInventario(**movimiento.model_dump())
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return {"id": registro.id}


@router.put("/movimientos/{movimiento_id}", response_model=MovimientoInventarioResponse)
def update_movimiento(
    movimiento_id: int,
    movimiento: MovimientoInventarioUpdate,
    db: Session = Depends(get_db),
):
    registro = db.get(MovimientoInventario, movimiento_id)
    if not registro:
        raise HTTPException(status_code=404, detail="El movimiento no existe.")

    if not registro.editable:
        raise HTTPException(
            status_code=400,
            detail="No se puede modificar un movimiento generado automáticamente por una guía o liquidación.",
        )

    if movimiento.tipo not in (
        TipoMovimientoInventario.STOCK_INICIAL,
        TipoMovimientoInventario.INGRESO,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden registrar manualmente stock inicial o ingresos.",
        )
    if movimiento.cantidad <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cantidad debe ser mayor que cero.",
        )

    registro.tipo = movimiento.tipo
    registro.cantidad = movimiento.cantidad
    registro.fecha = movimiento.fecha
    registro.observacion = movimiento.observacion

    db.commit()
    db.refresh(registro)
    return registro
