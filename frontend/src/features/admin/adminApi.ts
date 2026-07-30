/**
 * Cliente HTTP dedicado para el subsistema Administrador.
 * Lee `admin_token` de localStorage (no `access_token` del sistema de usuario).
 * En caso de 401, redirige al login de admin — nunca al login de usuario.
 */

const BASE_URL = "/access_role";
const ADMIN_LOGIN_PATH = "/access_role/admin/developer";

export class AdminApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = "AdminApiError";
  }
}

function getAdminToken(): string | null {
  return localStorage.getItem("admin_token");
}

function redirectToAdminLogin(): never {
  localStorage.removeItem("admin_token");
  window.location.href = ADMIN_LOGIN_PATH;
  throw new AdminApiError("Sesión de admin expirada", 401);
}

async function adminRequest<T>(
  method: string,
  path: string,
  body?: unknown
): Promise<T> {
  const headers: Record<string, string> = {};
  const token = getAdminToken();

  if (!token) {
    redirectToAdminLogin();
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
    redirectToAdminLogin();
  }

  if (res.status === 204) return undefined as T;

  if (!res.ok) {
    const data = await res.json().catch(() => ({
      detail: `Error del servidor (${res.status})`,
    }));
    throw new AdminApiError(data.detail, res.status);
  }

  return res.json();
}

export function adminGet<T>(path: string) {
  return adminRequest<T>("GET", path);
}

export async function adminGetBlob(path: string): Promise<Blob> {
  const headers: Record<string, string> = {};
  const token = getAdminToken();

  if (!token) {
    redirectToAdminLogin();
  }

  headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}`, {
    method: "GET",
    headers,
  });

  if (res.status === 401) {
    redirectToAdminLogin();
  }

  if (!res.ok) {
    const data = await res.json().catch(() => ({
      detail: `Error del servidor (${res.status})`,
    }));
    throw new AdminApiError(data.detail, res.status);
  }

  return res.blob();
}

export function adminPost<T>(path: string, body: unknown) {
  return adminRequest<T>("POST", path, body);
}
