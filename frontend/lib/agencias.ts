import { apiGet, apiSend, buildQuery } from "./http";

export { ApiError } from "./http";

export type Estado = "ACTIVO" | "INACTIVO";

export type AgenciaListItem = {
  id: number;
  codigo: string;
  nombre: string;
  propietario: string | null;
  agente: string | null;
  telefono: string | null;
  estado: Estado;
};

export type Agencia = AgenciaListItem & {
  direccion: string | null;
  created_at: string;
  updated_at: string;
};

export type AgenciaInput = {
  nombre: string;
  propietario?: string;
  agente?: string;
  telefono?: string;
  direccion?: string;
};

export type AgenciaFiltros = {
  nombre?: string;
  propietario?: string;
  estado?: Estado;
};

export function listarAgencias(filtros: AgenciaFiltros = {}): Promise<AgenciaListItem[]> {
  return apiGet(`/agencias${buildQuery(filtros)}`);
}

export function obtenerAgencia(id: number): Promise<Agencia> {
  return apiGet(`/agencias/${id}`);
}

export function crearAgencia(data: AgenciaInput): Promise<Agencia> {
  return apiSend("POST", "/agencias", data);
}

export function actualizarAgencia(id: number, data: AgenciaInput): Promise<Agencia> {
  return apiSend("PUT", `/agencias/${id}`, data);
}

export function darDeBajaAgencia(id: number): Promise<Agencia> {
  return apiSend("PATCH", `/agencias/${id}/dar-baja`);
}

export function reactivarAgencia(id: number): Promise<Agencia> {
  return apiSend("PATCH", `/agencias/${id}/reactivar`);
}
