import { apiGet, apiSend } from "./http";

export { ApiError } from "./http";

export type EstadoGuia =
  | "EN_VENTA"
  | "PENDIENTE_LIQUIDACION"
  | "PARCIALMENTE_LIQUIDADA"
  | "LIQUIDADA"
  | "ANULADA";

export type LiquidacionActivaInfo = {
  liquidacion_id: number;
  cantidad_vendida: number;
  fecha_liquidacion: string;
};

export type DetalleGuia = {
  id: number;
  producto_id: number;
  cantidad: number;
  precio: number | null;
  porcentaje_cobro: number | null;
  liquidaciones_activas: LiquidacionActivaInfo[];
};

export type Guia = {
  id: number;
  numero_guia: string;
  fecha: string;
  agencia_id: number;
  estado: EstadoGuia;
  observacion: string | null;
  detalles: DetalleGuia[];
};

export type DetalleGuiaInput = {
  producto_id: number;
  cantidad: number;
  precio: number;
  porcentaje_cobro: number;
};

export type GuiaCreateInput = {
  fecha: string;
  agencia_id: number;
  observacion?: string;
  detalles: DetalleGuiaInput[];
};

export type DetalleGuiaUpdateInput = {
  detalle_guia_id?: number;
  producto_id: number;
  cantidad: number;
  precio: number;
  porcentaje_cobro: number;
};

export type GuiaUpdateInput = {
  fecha?: string;
  observacion?: string;
  detalles?: DetalleGuiaUpdateInput[];
};

export function listarGuias(): Promise<Guia[]> {
  return apiGet(`/guias`);
}

export function obtenerGuia(id: number): Promise<Guia> {
  return apiGet(`/guias/${id}`);
}

export function crearGuia(data: GuiaCreateInput): Promise<Guia> {
  return apiSend("POST", "/guias", data);
}

export function actualizarGuia(id: number, data: GuiaUpdateInput): Promise<Guia> {
  return apiSend("PUT", `/guias/${id}`, data);
}

export function anularGuia(id: number): Promise<{ message: string }> {
  return apiSend("DELETE", `/guias/${id}`);
}

export const ESTADO_GUIA_LABEL: Record<EstadoGuia, string> = {
  EN_VENTA: "En venta",
  PENDIENTE_LIQUIDACION: "Pendiente de liquidación",
  PARCIALMENTE_LIQUIDADA: "Parcialmente liquidada",
  LIQUIDADA: "Liquidada",
  ANULADA: "Anulada",
};

export const ESTADO_GUIA_BADGE: Record<EstadoGuia, string> = {
  EN_VENTA: "badge-info",
  PENDIENTE_LIQUIDACION: "badge-warn",
  PARCIALMENTE_LIQUIDADA: "badge-warn",
  LIQUIDADA: "badge-ok",
  ANULADA: "badge-off",
};
