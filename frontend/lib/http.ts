const TOKEN_KEY = "sidec_token";

export class ApiError extends Error {}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return window.localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string): void {
  try {
    window.localStorage.setItem(TOKEN_KEY, token);
  } catch {
    // almacenamiento no disponible, la sesión no persistirá al recargar
  }
}

export function clearToken(): void {
  try {
    window.localStorage.removeItem(TOKEN_KEY);
  } catch {
    // almacenamiento no disponible
  }
}

function authHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function parseResponse<T>(res: Response): Promise<T> {
  if (res.ok) {
    return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
  }

  if (res.status === 401 && typeof window !== "undefined") {
    clearToken();
    window.dispatchEvent(new Event("sidec:auth-expired"));
  }

  let mensaje = `Error ${res.status}`;
  try {
    const body = await res.json();
    if (typeof body?.message === "string") {
      mensaje = body.message;
    } else if (Array.isArray(body?.detail)) {
      mensaje = body.detail
        .map((item: { loc?: string[]; msg?: string }) =>
          [item.loc?.at(-1), item.msg].filter(Boolean).join(": ")
        )
        .join(" | ");
    } else if (typeof body?.detail === "string") {
      mensaje = body.detail;
    }
  } catch {
    // respuesta sin cuerpo JSON, se conserva el mensaje genérico
  }
  throw new ApiError(mensaje);
}

export function buildQuery(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") search.set(key, String(value));
  }
  const query = search.toString();
  return query ? `?${query}` : "";
}

export function apiGet<T>(path: string): Promise<T> {
  return fetch(`/api${path}`, { headers: authHeaders() }).then((res) => parseResponse<T>(res));
}

export function apiSend<T>(
  method: "POST" | "PUT" | "PATCH" | "DELETE",
  path: string,
  data?: unknown
): Promise<T> {
  return fetch(`/api${path}`, {
    method,
    headers: {
      ...authHeaders(),
      ...(data !== undefined ? { "Content-Type": "application/json" } : {}),
    },
    body: data !== undefined ? JSON.stringify(data) : undefined,
  }).then((res) => parseResponse<T>(res));
}
