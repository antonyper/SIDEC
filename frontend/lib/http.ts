export class ApiError extends Error {}

export async function parseResponse<T>(res: Response): Promise<T> {
  if (res.ok) {
    return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
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
  return fetch(`/api${path}`).then((res) => parseResponse<T>(res));
}

export function apiSend<T>(
  method: "POST" | "PUT" | "PATCH" | "DELETE",
  path: string,
  data?: unknown
): Promise<T> {
  return fetch(`/api${path}`, {
    method,
    headers: data !== undefined ? { "Content-Type": "application/json" } : undefined,
    body: data !== undefined ? JSON.stringify(data) : undefined,
  }).then((res) => parseResponse<T>(res));
}
