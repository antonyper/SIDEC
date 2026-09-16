import { apiGet, apiSend } from "./http";

export { ApiError } from "./http";

export type TipoMovimientoInventario =
  | "STOCK_INICIAL"
  | "INGRESO"
  | "SALIDA_GUIA"
  | "DEVOLUCION";

export type InventarioItem = {
  producto_id: number;
  codigo: string;
  producto: string;
  stock: number;
};

export type MovimientoInventarioInput = {
  producto_id: number;
  tipo: TipoMovimientoInventario;
  cantidad: number;
  fecha: string;
  observacion?: string;
};

export type MovimientoInventario = {
  id: number;
  tipo: TipoMovimientoInventario;
  cantidad: number;
  fecha: string;
  observacion: string | null;
  editable: boolean;
};

export type MovimientoInventarioUpdateInput = {
  tipo: TipoMovimientoInventario;
  cantidad: number;
  fecha: string;
  observacion?: string;
};

export function listarInventario(): Promise<InventarioItem[]> {
  return apiGet(`/inventario`);
}

export function listarMovimientosPorProducto(productoId: number): Promise<MovimientoInventario[]> {
  return apiGet(`/inventario/${productoId}/movimientos`);
}

export function registrarMovimiento(data: MovimientoInventarioInput): Promise<{ id: number }> {
  return apiSend("POST", "/inventario/movimientos", data);
}

export function actualizarMovimiento(
  id: number,
  data: MovimientoInventarioUpdateInput
): Promise<MovimientoInventario> {
  return apiSend("PUT", `/inventario/movimientos/${id}`, data);
}

export const TIPO_MOVIMIENTO_LABEL: Record<TipoMovimientoInventario, string> = {
  STOCK_INICIAL: "Stock inicial",
  INGRESO: "Ingreso",
  SALIDA_GUIA: "Entrega a agencia",
  DEVOLUCION: "Devolución",
};

export const TIPO_MOVIMIENTO_SIGNO: Record<TipoMovimientoInventario, 1 | -1> = {
  STOCK_INICIAL: 1,
  INGRESO: 1,
  SALIDA_GUIA: -1,
  DEVOLUCION: 1,
};
