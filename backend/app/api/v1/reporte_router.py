from datetime import date

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.enums.estado_guia import EstadoGuia
from app.repositories.reporte_repository import ReporteRepository
from app.services.pdf_service import generar_pdf_detalle_por_agencia
from app.schemas.reporte_schema import (
    CobranzaPeriodoItem,
    DesempenoAgenciaItem,
    DetalleAgenciaResponse,
    DeudaPendienteResponse,
    DistribucionResponse,
    GuiaPendienteItem,
    GuiaPorVencerItem,
    KardexInventarioItem,
    RankingAgenciaItem,
    ReporteAgenciaItem,
    ReporteProductoItem,
    ResumenGuiasResponse,
    ResumenPeriodoResponse,
    TopAgenciaProductoItem,
)

router = APIRouter(prefix="/reportes", tags=["Reportes"])


def get_repository(db: Session = Depends(get_db)) -> ReporteRepository:
    return ReporteRepository(db)


@router.get(
    "/cobranzas-por-periodo",
    response_model=list[CobranzaPeriodoItem],
    description="Cobranzas generadas en un rango de fechas (por fecha de liquidación).",
)
def cobranzas_por_periodo(
    desde: date | None = None,
    hasta: date | None = None,
    repository: ReporteRepository = Depends(get_repository),
):
    return repository.cobranzas_por_periodo(desde, hasta)


@router.get(
    "/guias-pendientes",
    response_model=list[GuiaPendienteItem],
    description="Guías en estado pendiente (aún no vencidas para liquidación).",
)
def guias_pendientes(repository: ReporteRepository = Depends(get_repository)):
    return repository.guias_por_estados([EstadoGuia.EN_VENTA])


@router.get(
    "/guias-pendientes-liquidacion",
    response_model=list[GuiaPendienteItem],
    description="Guías pendientes o parcialmente liquidadas.",
)
def guias_pendientes_liquidacion(repository: ReporteRepository = Depends(get_repository)):
    return repository.guias_por_estados(
        [EstadoGuia.PENDIENTE_LIQUIDACION, EstadoGuia.PARCIALMENTE_LIQUIDADA]
    )


@router.get(
    "/resumen-guias",
    response_model=ResumenGuiasResponse,
    description="Cantidad de guías por estado y valor total entregado.",
)
def resumen_guias(repository: ReporteRepository = Depends(get_repository)):
    return repository.resumen_guias()


@router.get(
    "/desempeno-agencias",
    response_model=list[DesempenoAgenciaItem],
    description="Ventas, cobros y deuda pendiente por agencia.",
)
def desempeno_agencias(
    desde: date | None = None,
    hasta: date | None = None,
    repository: ReporteRepository = Depends(get_repository),
):
    return repository.desempeno_agencias(desde, hasta)


@router.get(
    "/deuda-pendiente",
    response_model=DeudaPendienteResponse,
    description="Cobranzas con saldo pendiente, ordenadas por antigüedad.",
)
def deuda_pendiente(repository: ReporteRepository = Depends(get_repository)):
    return repository.deuda_pendiente()


@router.get(
    "/por-producto",
    response_model=list[ReporteProductoItem],
    description="Cantidad entregada, vendida, ingresos y stock por producto.",
)
def reporte_por_producto(repository: ReporteRepository = Depends(get_repository)):
    return repository.reporte_por_producto()


@router.get(
    "/agencias",
    response_model=list[ReporteAgenciaItem],
    description="Directorio de agencias con totales de guías.",
)
def reporte_agencias(repository: ReporteRepository = Depends(get_repository)):
    return repository.reporte_agencias()


@router.get(
    "/resumen-periodo",
    response_model=ResumenPeriodoResponse,
    description="Resumen general del negocio en un rango de fechas.",
)
def resumen_periodo(
    desde: date | None = None,
    hasta: date | None = None,
    repository: ReporteRepository = Depends(get_repository),
):
    return repository.resumen_periodo(desde, hasta)


@router.get(
    "/kardex-inventario",
    response_model=list[KardexInventarioItem],
    description="Todos los movimientos de inventario (entregas, devoluciones, ingresos), filtrable por producto y fecha.",
)
def kardex_inventario(
    producto_id: int | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    repository: ReporteRepository = Depends(get_repository),
):
    return repository.kardex_inventario(producto_id, desde, hasta)


@router.get(
    "/ranking-agencias-venta",
    response_model=list[RankingAgenciaItem],
    description="Ranking de agencias por porcentaje de venta (vendido sobre lo entregado).",
)
def ranking_agencias_venta(
    desde: date | None = None,
    hasta: date | None = None,
    repository: ReporteRepository = Depends(get_repository),
):
    return repository.ranking_agencias_venta(desde, hasta)


@router.get(
    "/guias-por-vencer",
    response_model=list[GuiaPorVencerItem],
    description="Guías en venta con los días restantes antes de pasar a pendiente de liquidación.",
)
def guias_por_vencer(repository: ReporteRepository = Depends(get_repository)):
    return repository.guias_por_vencer()


@router.get(
    "/distribucion",
    response_model=DistribucionResponse,
    description="Matriz de cantidad distribuida por agencia y producto (excluye guías anuladas).",
)
def reporte_distribucion(
    desde: date | None = None,
    hasta: date | None = None,
    producto_id: list[int] | None = Query(default=None),
    repository: ReporteRepository = Depends(get_repository),
):
    return repository.reporte_distribucion(desde, hasta, producto_id)


@router.get(
    "/detalle-por-agencia",
    response_model=DetalleAgenciaResponse,
    description="Detalle de productos entregados por agencia, con el estimado (50% de precio agencia).",
)
def detalle_por_agencia(
    desde: date | None = None,
    hasta: date | None = None,
    repository: ReporteRepository = Depends(get_repository),
):
    return repository.detalle_por_agencia(desde, hasta)


@router.get(
    "/detalle-por-agencia/pdf",
    description="Descarga el reporte 'Detalle por agencia' como PDF.",
)
def detalle_por_agencia_pdf(
    desde: date | None = None,
    hasta: date | None = None,
    repository: ReporteRepository = Depends(get_repository),
):
    data = repository.detalle_por_agencia(desde, hasta)
    pdf_bytes = generar_pdf_detalle_por_agencia(data, desde, hasta)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="detalle-por-agencia.pdf"'},
    )


@router.get(
    "/top-agencias-productos",
    response_model=list[TopAgenciaProductoItem],
    description="Ranking de agencias por cantidad de productos distintos que reciben (excluye guías anuladas).",
)
def top_agencias_por_productos(repository: ReporteRepository = Depends(get_repository)):
    return repository.top_agencias_por_productos()
