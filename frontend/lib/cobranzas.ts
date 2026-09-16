import { apiGet, apiSend } from "./http";

export { ApiError } from "./http";

export type EstadoCobranza = "PENDIENTE" | "COBRADO" | "ANULADA";

export type Cobranza = {
  id: number;
  liquidacion_id: number;
  agencia_nombre: string | null;
  monto: number;
  monto_pagado: number;
  monto_pendiente: number;
  estado: EstadoCobranza;
};

export function listarCobranzas(): Promise<Cobranza[]> {
  return apiGet(`/cobranzas`);
}

export function obtenerCobranza(id: number): Promise<Cobranza> {
  return apiGet(`/cobranzas/${id}`);
}

export function obtenerCobranzaPorLiquidacion(liquidacionId: number): Promise<Cobranza> {
  return apiGet(`/cobranzas/liquidacion/${liquidacionId}`);
}

export function registrarPago(id: number, montoPagado: number): Promise<Cobranza> {
  return apiSend("PUT", `/cobranzas/${id}`, { monto_pagado: montoPagado });
}

export const ESTADO_COBRANZA_LABEL: Record<EstadoCobranza, string> = {
  PENDIENTE: "Pendiente",
  COBRADO: "Cobrado",
  ANULADA: "Anulada",
};

export const ESTADO_COBRANZA_BADGE: Record<EstadoCobranza, string> = {
  PENDIENTE: "badge-warn",
  COBRADO: "badge-ok",
  ANULADA: "badge-off",
};
