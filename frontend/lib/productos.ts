import { apiGet, apiSend, buildQuery } from "./http";

export { ApiError } from "./http";

export type Estado = "ACTIVO" | "INACTIVO";

export type ProductoListItem = {
  id: number;
  codigo: string;
  nombre: string;
  categoria: string | null;
  precio: number | null;
  estado: Estado;
};

export type Producto = ProductoListItem & {
  created_at: string;
  updated_at: string;
};

export type ProductoInput = {
  nombre: string;
  categoria?: string;
  precio?: number;
};

export type ProductoFiltros = {
  nombre?: string;
  categoria?: string;
  estado?: Estado;
  buscar?: string;
};

export function listarProductos(filtros: ProductoFiltros = {}): Promise<ProductoListItem[]> {
  return apiGet(`/productos${buildQuery(filtros)}`);
}

export function obtenerProducto(id: number): Promise<Producto> {
  return apiGet(`/productos/${id}`);
}

export function crearProducto(data: ProductoInput): Promise<Producto> {
  return apiSend("POST", "/productos", data);
}

export function actualizarProducto(id: number, data: ProductoInput): Promise<Producto> {
  return apiSend("PUT", `/productos/${id}`, data);
}

export function darDeBajaProducto(id: number): Promise<Producto> {
  return apiSend("PATCH", `/productos/${id}/dar-baja`);
}

export function reactivarProducto(id: number): Promise<Producto> {
  return apiSend("PATCH", `/productos/${id}/reactivar`);
}

export function eliminarProducto(id: number): Promise<{ message: string }> {
  return apiSend("DELETE", `/productos/${id}`);
}
