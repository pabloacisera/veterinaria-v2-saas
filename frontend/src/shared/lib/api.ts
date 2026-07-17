const BASE_URL = "/api/v1";

interface ApiError {
  detail: string;
}

export class ApiClientError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = "ApiClientError";
  }
}

function getToken(): string | null {
  return localStorage.getItem("access_token");
}

let isRefreshing = false;

async function tryRefresh(): Promise<boolean> {
  if (isRefreshing) return false;
  isRefreshing = true;
  try {
    const res = await fetch(`${BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    });
    if (!res.ok) return false;
    const data = await res.json();
    if (data.access_token) {
      localStorage.setItem("access_token", data.access_token);
    }
    return true;
  } catch {
    return false;
  } finally {
    isRefreshing = false;
  }
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown
): Promise<T> {
  const headers: Record<string, string> = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  if (body && !(body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  let res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    credentials: "include",
    body: body
      ? body instanceof FormData
        ? body
        : JSON.stringify(body)
      : undefined,
  });

  if (res.status === 401 && path !== "/auth/refresh") {
    const refreshed = await tryRefresh();
    if (refreshed) {
      const newToken = getToken();
      if (newToken) headers["Authorization"] = `Bearer ${newToken}`;
      res = await fetch(`${BASE_URL}${path}`, {
        method,
        headers,
        credentials: "include",
        body: body
          ? body instanceof FormData
            ? body
            : JSON.stringify(body)
          : undefined,
      });
    } else {
      window.location.href = "/login";
      throw new ApiClientError("Sesión expirada", 401);
    }
  }

  if (res.status === 204) return undefined as T;

  if (!res.ok) {
    const data: ApiError = await res.json().catch(() => ({
      detail: `Error del servidor (${res.status})`,
    }));
    throw new ApiClientError(data.detail, res.status);
  }

  return res.json();
}

export function apiGet<T>(path: string) {
  return request<T>("GET", path);
}

export async function apiGetBlob(path: string): Promise<Blob> {
  const headers: Record<string, string> = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let res = await fetch(`${BASE_URL}${path}`, { method: "GET", headers, credentials: "include" });

  if (res.status === 401 && path !== "/auth/refresh") {
    const refreshed = await tryRefresh();
    if (refreshed) {
      const newToken = getToken();
      if (newToken) headers["Authorization"] = `Bearer ${newToken}`;
      res = await fetch(`${BASE_URL}${path}`, { method: "GET", headers, credentials: "include" });
    } else {
      window.location.href = "/login";
      throw new ApiClientError("Sesión expirada", 401);
    }
  }

  if (!res.ok) {
    const data: ApiError = await res.json().catch(() => ({
      detail: `Error del servidor (${res.status})`,
    }));
    throw new ApiClientError(data.detail, res.status);
  }

  return res.blob();
}

export function apiPost<T>(path: string, body: unknown) {
  return request<T>("POST", path, body);
}

export function apiPut<T>(path: string, body: unknown) {
  return request<T>("PUT", path, body);
}

export function apiPatch<T>(path: string, body: unknown) {
  return request<T>("PATCH", path, body);
}

export function apiDelete(path: string) {
  return request<void>("DELETE", path);
}
