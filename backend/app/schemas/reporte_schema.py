from datetime import date
from decimal import Decimal

from app.schemas.base_schema import BaseSchema


class CobranzaPeriodoItem(BaseSchema):
    liquidacion_id: int
    fecha: date
    agencia: str
    monto: Decimal
    monto_pagado: Decimal
    monto_pendiente: Decimal
    estado: str


class GuiaPendienteItem(BaseSchema):
    guia_id: int
    numero_guia: str
    fecha: date
    agencia: str
    estado: str
    dias_transcurridos: int


class ResumenGuiasItem(BaseSchema):
    estado: str
    cantidad: int


class ResumenGuiasResponse(BaseSchema):
    total_guias: int
    por_estado: list[ResumenGuiasItem]
    valor_total_entregado: Decimal


class DesempenoAgenciaItem(BaseSchema):
    agencia_id: int
    agencia: str
    estado: str
    total_guias: int
    total_vendido: Decimal
    total_cobrado: Decimal
    deuda_pendiente: Decimal


class DeudaPendienteItem(BaseSchema):
    cobranza_id: int
    liquidacion_id: int
    guia_id: int
    numero_guia: str
    agencia: str
    fecha: date
    monto_pendiente: Decimal
    dias_pendiente: int


class DeudaPendienteResponse(BaseSchema):
    total_pendiente: Decimal
    items: list[DeudaPendienteItem]


class ReporteProductoItem(BaseSchema):
    producto_id: int
    codigo: str
    producto: str
    cantidad_entregada: int
    cantidad_vendida: int
    porcentaje_venta: Decimal
    ingresos: Decimal
    stock_actual: Decimal


class ReporteAgenciaItem(BaseSchema):
    agencia_id: int
    codigo: str
    agencia: str
    propietario: str | None = None
    agente: str | None = None
    telefono: str | None = None
    estado: str
    total_guias: int
    guias_activas: int


class ResumenPeriodoResponse(BaseSchema):
    desde: date | None = None
    hasta: date | None = None
    guias_emitidas: int
    valor_entregado: Decimal
    total_liquidado: Decimal
    total_cobrado: Decimal
    total_pendiente: Decimal


class KardexInventarioItem(BaseSchema):
    fecha: date
    producto_id: int
    producto: str
    tipo: str
    cantidad: Decimal
    observacion: str | None = None


class RankingAgenciaItem(BaseSchema):
    agencia_id: int
    agencia: str
    unidades_entregadas: int
    unidades_vendidas: int
    unidades_devueltas: int
    porcentaje_venta: Decimal


class GuiaPorVencerItem(BaseSchema):
    guia_id: int
    numero_guia: str
    fecha: date
    agencia: str
    dias_transcurridos: int
    dias_restantes: int


class DistribucionColumna(BaseSchema):
    producto_id: int
    producto: str
    total: int


class DistribucionFila(BaseSchema):
    agencia_id: int
    agencia: str
    total: int
    valores: list[int]


class DistribucionResponse(BaseSchema):
    columnas: list[DistribucionColumna]
    filas: list[DistribucionFila]
    total_general: int


class DetalleAgenciaItem(BaseSchema):
    guia_id: int
    numero_guia: str
    fecha: date
    estado_guia: str
    producto_id: int
    producto: str
    cantidad: int
    precio_publico: Decimal
    precio_agencia: Decimal
    x_estimado: Decimal


class DetalleAgenciaGrupo(BaseSchema):
    agencia_id: int
    agencia: str
    detalles: list[DetalleAgenciaItem]
    total_entregado: Decimal


class DetalleAgenciaResponse(BaseSchema):
    grupos: list[DetalleAgenciaGrupo]
    total_general: Decimal


class TopAgenciaProductoItem(BaseSchema):
    agencia_id: int
    agencia: str
    cantidad_productos: int
