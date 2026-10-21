import { apiGet, buildQuery, ApiError, getToken } from "./http";

export { ApiError } from "./http";

export type RangoFechas = { desde?: string; hasta?: string };

export type CobranzaPeriodoItem = {
  liquidacion_id: number;
  fecha: string;
  agencia: string;
  monto: number;
  monto_pagado: number;
  monto_pendiente: number;
  estado: string;
};

export type GuiaPendienteItem = {
  guia_id: number;
  numero_guia: string;
  fecha: string;
  agencia: string;
  estado: string;
  dias_transcurridos: number;
};

export type ResumenGuiasResponse = {
  total_guias: number;
  por_estado: { estado: string; cantidad: number }[];
  valor_total_entregado: number;
};

export type DesempenoAgenciaItem = {
  agencia_id: number;
  agencia: string;
  estado: string;
  total_guias: number;
  total_vendido: number;
  total_cobrado: number;
  deuda_pendiente: number;
};

export type DeudaPendienteItem = {
  cobranza_id: number;
  liquidacion_id: number;
  guia_id: number;
  numero_guia: string;
  agencia: string;
  fecha: string;
  monto_pendiente: number;
  dias_pendiente: number;
};

export type DeudaPendienteResponse = {
  total_pendiente: number;
  items: DeudaPendienteItem[];
};

export type ReporteProductoItem = {
  producto_id: number;
  codigo: string;
  producto: string;
  cantidad_entregada: number;
  cantidad_vendida: number;
  porcentaje_venta: number;
  ingresos: number;
  stock_actual: number;
};

export type ReporteAgenciaItem = {
  agencia_id: number;
  codigo: string;
  agencia: string;
  propietario: string | null;
  agente: string | null;
  telefono: string | null;
  estado: string;
  total_guias: number;
  guias_activas: number;
};

export type ResumenPeriodoResponse = {
  desde: string | null;
  hasta: string | null;
  guias_emitidas: number;
  valor_entregado: number;
  total_liquidado: number;
  total_cobrado: number;
  total_pendiente: number;
};

export function reporteCobranzasPorPeriodo(rango: RangoFechas): Promise<CobranzaPeriodoItem[]> {
  return apiGet(`/reportes/cobranzas-por-periodo${buildQuery(rango)}`);
}

export function reporteGuiasPendientes(): Promise<GuiaPendienteItem[]> {
  return apiGet(`/reportes/guias-pendientes`);
}

export function reporteGuiasPendientesLiquidacion(): Promise<GuiaPendienteItem[]> {
  return apiGet(`/reportes/guias-pendientes-liquidacion`);
}

export function reporteResumenGuias(): Promise<ResumenGuiasResponse> {
  return apiGet(`/reportes/resumen-guias`);
}

export function reporteDesempenoAgencias(rango: RangoFechas): Promise<DesempenoAgenciaItem[]> {
  return apiGet(`/reportes/desempeno-agencias${buildQuery(rango)}`);
}

export function reporteDeudaPendiente(): Promise<DeudaPendienteResponse> {
  return apiGet(`/reportes/deuda-pendiente`);
}

export function reportePorProducto(): Promise<ReporteProductoItem[]> {
  return apiGet(`/reportes/por-producto`);
}

export function reporteAgencias(): Promise<ReporteAgenciaItem[]> {
  return apiGet(`/reportes/agencias`);
}

export function reporteResumenPeriodo(rango: RangoFechas): Promise<ResumenPeriodoResponse> {
  return apiGet(`/reportes/resumen-periodo${buildQuery(rango)}`);
}

export type KardexInventarioItem = {
  fecha: string;
  producto_id: number;
  producto: string;
  tipo: string;
  cantidad: number;
  observacion: string | null;
};

export type KardexFiltro = RangoFechas & { producto_id?: number };

export function reporteKardexInventario(filtro: KardexFiltro): Promise<KardexInventarioItem[]> {
  return apiGet(`/reportes/kardex-inventario${buildQuery(filtro)}`);
}

export type RankingAgenciaItem = {
  agencia_id: number;
  agencia: string;
  unidades_entregadas: number;
  unidades_vendidas: number;
  unidades_devueltas: number;
  porcentaje_venta: number;
};

export function reporteRankingAgenciasVenta(rango: RangoFechas): Promise<RankingAgenciaItem[]> {
  return apiGet(`/reportes/ranking-agencias-venta${buildQuery(rango)}`);
}

export type GuiaPorVencerItem = {
  guia_id: number;
  numero_guia: string;
  fecha: string;
  agencia: string;
  dias_transcurridos: number;
  dias_restantes: number;
};

export function reporteGuiasPorVencer(): Promise<GuiaPorVencerItem[]> {
  return apiGet(`/reportes/guias-por-vencer`);
}

export type DistribucionColumna = {
  producto_id: number;
  producto: string;
  total: number;
};

export type DistribucionFila = {
  agencia_id: number;
  agencia: string;
  total: number;
  valores: number[];
};

export type DistribucionResponse = {
  columnas: DistribucionColumna[];
  filas: DistribucionFila[];
  total_general: number;
};

export type DistribucionFiltro = RangoFechas & { producto_ids?: number[] };

export function reporteDistribucion(filtro: DistribucionFiltro): Promise<DistribucionResponse> {
  const params = new URLSearchParams();
  if (filtro.desde) params.set("desde", filtro.desde);
  if (filtro.hasta) params.set("hasta", filtro.hasta);
  for (const id of filtro.producto_ids ?? []) {
    params.append("producto_id", String(id));
  }
  const query = params.toString();
  return apiGet(`/reportes/distribucion${query ? `?${query}` : ""}`);
}

export type DetalleAgenciaItem = {
  guia_id: number;
  numero_guia: string;
  fecha: string;
  estado_guia: string;
  producto_id: number;
  producto: string;
  cantidad: number;
  precio_publico: number;
  precio_agencia: number;
  x_estimado: number;
};

export type DetalleAgenciaGrupo = {
  agencia_id: number;
  agencia: string;
  detalles: DetalleAgenciaItem[];
  total_entregado: number;
};

export type DetalleAgenciaResponse = {
  grupos: DetalleAgenciaGrupo[];
  total_general: number;
};

export function reporteDetallePorAgencia(rango: RangoFechas): Promise<DetalleAgenciaResponse> {
  return apiGet(`/reportes/detalle-por-agencia${buildQuery(rango)}`);
}

export async function descargarDetallePorAgenciaPdf(rango: RangoFechas): Promise<void> {
  const token = getToken();
  const res = await fetch(`/api/reportes/detalle-por-agencia/pdf${buildQuery(rango)}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  });
  if (!res.ok) {
    throw new ApiError("No se pudo generar el PDF.");
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const enlace = document.createElement("a");
  enlace.href = url;
  enlace.download = "detalle-por-agencia.pdf";
  enlace.click();
  URL.revokeObjectURL(url);
}

export type TopAgenciaProductoItem = {
  agencia_id: number;
  agencia: string;
  cantidad_productos: number;
};

export function reporteTopAgenciasProductos(): Promise<TopAgenciaProductoItem[]> {
  return apiGet(`/reportes/top-agencias-productos`);
}
