/**
 * Cliente HTTP dedicado para el portal de clientes (dueños de mascotas).
 * Lee `client_token` de localStorage (no `access_token` del sistema de usuario).
 * En caso de 401, redirige al acceso del portal — nunca al login de veterinario.
 */

const BASE_URL = "/api/v1";
const CLIENT_LOGIN_PATH = "/cliente/acceso";

export class ClientApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = "ClientApiError";
  }
}

function getClientToken(): string | null {
  return localStorage.getItem("client_token");
}

function redirectToClientAccess(): never {
  localStorage.removeItem("client_token");
  window.location.href = CLIENT_LOGIN_PATH;
  throw new ClientApiError("Sesión de cliente expirada", 401);
}

async function clientRequest<T>(
  method: string,
  path: string,
  body?: unknown
): Promise<T> {
  const headers: Record<string, string> = {};
  const token = getClientToken();

  if (!token) {
    redirectToClientAccess();
  }

  headers["Authorization"] = `Bearer ${token}`;

  if (body && !(body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body
      ? body instanceof FormData
        ? body
        : JSON.stringify(body)
      : undefined,
  });

  if (res.status === 401) {
    redirectToClientAccess();
  }

  if (res.status === 204) return undefined as T;

  if (!res.ok) {
    const data = await res.json().catch(() => ({
      detail: `Error del servidor (${res.status})`,
    }));
    throw new ClientApiError(data.detail, res.status);
  }

  return res.json();
}

export function clientGet<T>(path: string) {
  return clientRequest<T>("GET", path);
}

export function clientPost<T>(path: string, body: unknown) {
  return clientRequest<T>("POST", path, body);
}
