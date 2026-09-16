import { apiGet, apiSend, clearToken, setToken } from "./http";

export { ApiError } from "./http";

export type RolUsuario = "ADMIN" | "OPERADOR";

export type Usuario = {
  id: number;
  nombre: string;
  username: string;
  rol: RolUsuario;
  activo: boolean;
  created_at: string;
};

export type UsuarioInput = {
  nombre: string;
  username: string;
  password: string;
  rol: RolUsuario;
};

export type UsuarioUpdateInput = {
  nombre?: string;
  password?: string;
  rol?: RolUsuario;
};

type TokenResponse = {
  access_token: string;
  token_type: string;
  usuario: Usuario;
};

export async function login(username: string, password: string): Promise<Usuario> {
  const data = await apiSend<TokenResponse>("POST", "/auth/login", { username, password });
  setToken(data.access_token);
  return data.usuario;
}

export function logout(): void {
  clearToken();
}

export function obtenerUsuarioActual(): Promise<Usuario> {
  return apiGet("/auth/me");
}

export function listarUsuarios(): Promise<Usuario[]> {
  return apiGet("/usuarios");
}

export function crearUsuario(data: UsuarioInput): Promise<Usuario> {
  return apiSend("POST", "/usuarios", data);
}

export function actualizarUsuario(id: number, data: UsuarioUpdateInput): Promise<Usuario> {
  return apiSend("PUT", `/usuarios/${id}`, data);
}

export function darDeBajaUsuario(id: number): Promise<Usuario> {
  return apiSend("PATCH", `/usuarios/${id}/dar-baja`);
}

export function reactivarUsuario(id: number): Promise<Usuario> {
  return apiSend("PATCH", `/usuarios/${id}/reactivar`);
}
