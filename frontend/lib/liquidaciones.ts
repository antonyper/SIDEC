import { apiGet, apiSend } from "./http";

export { ApiError } from "./http";

export type EstadoLiquidacion = "LIQUIDADO" | "ANULADA";

export type DetalleLiquidacion = {
  id: number;
  detalle_guia_id: number;
  cantidad_vendida: number;
  cantidad_devuelta: number;
  total: number;
};

export type Liquidacion = {
  id: number;
  fecha: string;
  guia_id: number;
  estado: EstadoLiquidacion;
  observacion: string | null;
  detalles: DetalleLiquidacion[];
  created_at: string;
  updated_at: string;
};

export type LiquidacionListItem = {
  id: number;
  fecha: string;
  guia_id: number;
  estado: EstadoLiquidacion;
  observacion: string | null;
};

export type DetalleGuiaParaLiquidar = {
  detalle_guia_id: number;
  producto_id: number;
  producto: string;
  cantidad: number;
  precio: number;
  porcentaje_cobro: number;
  precio_a_liquidar: number;
};

export type GuiaParaLiquidar = {
  guia_id: number;
  numero_guia: string;
  fecha: string;
  agencia_id: number;
  agencia: string;
  detalles: DetalleGuiaParaLiquidar[];
};

export type DetalleLiquidacionInput = {
  detalle_guia_id: number;
  cantidad_devuelta: number;
  precio_a_liquidar?: number;
};

export type LiquidacionCreateInput = {
  fecha: string;
  guia_id: number;
  observacion?: string;
  detalles: DetalleLiquidacionInput[];
  pago_a_cuenta?: number;
};

export function listarLiquidaciones(): Promise<LiquidacionListItem[]> {
  return apiGet(`/liquidaciones`);
}

export function obtenerLiquidacion(id: number): Promise<Liquidacion> {
  return apiGet(`/liquidaciones/${id}`);
}

export function obtenerGuiaParaLiquidar(guiaId: number): Promise<GuiaParaLiquidar> {
  return apiGet(`/liquidaciones/guia/${guiaId}`);
}

export function crearLiquidacion(data: LiquidacionCreateInput): Promise<Liquidacion> {
  return apiSend("POST", "/liquidaciones", data);
}

export function anularLiquidacion(id: number): Promise<Liquidacion> {
  return apiSend("PATCH", `/liquidaciones/${id}/anular`);
}

export const ESTADO_LIQUIDACION_BADGE: Record<EstadoLiquidacion, string> = {
  LIQUIDADO: "badge-ok",
  ANULADA: "badge-off",
};

export const ESTADO_LIQUIDACION_LABEL: Record<EstadoLiquidacion, string> = {
  LIQUIDADO: "Liquidado",
  ANULADA: "Anulada",
};
