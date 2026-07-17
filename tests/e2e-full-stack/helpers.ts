import { APIRequestContext, Page } from "@playwright/test";
import Redis from "ioredis";

export const API_BASE =
  process.env.PLAYWRIGHT_API_URL || "http://localhost:8000/api/v1";

const REDIS_HOST = process.env.PLAYWRIGHT_REDIS_HOST || "localhost";
const REDIS_PORT = parseInt(process.env.PLAYWRIGHT_REDIS_PORT || "6379", 10);

export function randomEmail(): string {
  return `e2e_${Date.now()}_${Math.random().toString(36).slice(2, 8)}@test.com`;
}

export const TEST_PASSWORD = "Test123456!";

export function randomCuit(): string {
  return `20-${String(Math.floor(Math.random() * 10000000)).padStart(8, "0")}-9`;
}

export async function apiRegister(
  request: APIRequestContext,
  email: string,
  password: string,
) {
  const res = await request.post(`${API_BASE}/auth/register`, {
    data: {
      name: "Test",
      surname: "E2E",
      email,
      password,
      company_name: "Clinica E2E",
      cuit: randomCuit(),
    },
  });
  if (!res.ok()) throw new Error(`apiRegister failed: ${await res.text()}`);
  return res.json();
}

export async function getActivationCode(email: string): Promise<string> {
  const redis = new Redis({ host: REDIS_HOST, port: REDIS_PORT, db: 2 });
  try {
    const code = await redis.get(`activation:${email}`);
    if (!code) throw new Error(`No activation code found for ${email}`);
    return code;
  } finally {
    await redis.quit();
  }
}

export async function apiActivate(request: APIRequestContext, email: string) {
  const code = await getActivationCode(email);
  const res = await request.post(`${API_BASE}/auth/activate`, {
    data: { email, code },
  });
  if (!res.ok()) throw new Error(`apiActivate failed: ${await res.text()}`);
  return res.json();
}

export async function apiLogin(
  request: APIRequestContext,
  email: string,
  password: string,
) {
  const res = await request.post(`${API_BASE}/auth/login`, {
    data: { email, password },
  });
  if (!res.ok()) throw new Error(`apiLogin failed: ${await res.text()}`);
  return (await res.json()) as {
    access_token: string;
    refresh_token: string;
  };
}

export async function setupUser(
  request: APIRequestContext,
  email?: string,
  password?: string,
): Promise<{
  email: string;
  password: string;
  access_token: string;
  refresh_token: string;
}> {
  const e = email || randomEmail();
  const p = password || TEST_PASSWORD;
  await apiRegister(request, e, p);
  await apiActivate(request, e);
  const tokens = await apiLogin(request, e, p);
  return { email: e, password: p, ...tokens };
}

export function setTokens(page: Page, accessToken: string, refreshToken: string) {
  return page.evaluate(
    ({ at, rt }: { at: string; rt: string }) => {
      localStorage.setItem("access_token", at);
      localStorage.setItem("refresh_token", rt);
    },
    { at: accessToken, rt: refreshToken },
  );
}

export async function createClient(
  request: APIRequestContext,
  token: string,
  overrides?: Partial<{
    name: string;
    surname: string;
    email: string;
    doc_type: string;
    doc_number: string;
    phone: string;
  }>,
) {
  const data = {
    name: "María",
    surname: "García",
    email: `cliente_${Date.now()}@test.com`,
    doc_type: "DNI",
    doc_number: String(Math.floor(Math.random() * 100000000)),
    phone: "1144445555",
    ...overrides,
  };
  const res = await request.post(`${API_BASE}/clients`, {
    data,
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok()) throw new Error(`createClient failed: ${await res.text()}`);
  return (await res.json()) as { id: string; name: string; surname: string };
}

export async function createPet(
  request: APIRequestContext,
  token: string,
  ownerId: string,
  overrides?: Partial<{
    name: string;
    species: string;
    breed: string;
    sex: string;
    color: string;
    birth_date: string;
  }>,
) {
  const data = {
    owner_id: ownerId,
    name: "Firulais",
    species: "Perro",
    breed: "Labrador",
    sex: "Macho",
    color: "Dorado",
    birth_date: "2023-05-10",
    ...overrides,
  };
  const res = await request.post(`${API_BASE}/pets`, {
    data,
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok()) throw new Error(`createPet failed: ${await res.text()}`);
  return (await res.json()) as { id: string; name: string };
}

export async function createSupply(
  request: APIRequestContext,
  token: string,
  overrides?: Partial<{
    name: string;
    brand: string;
    unit_base: string;
    unit_price: number;
    stock_quantity: number;
  }>,
) {
  const data = {
    name: "Antipulgas",
    brand: "MarcaTest",
    unit_base: "unidad",
    unit_price: 2500,
    stock_quantity: 100,
    ...overrides,
  };
  const res = await request.post(`${API_BASE}/supplies`, {
    data,
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok()) throw new Error(`createSupply failed: ${await res.text()}`);
  return (await res.json()) as { id: string; name: string; unit_price: number };
}

export async function createProcedure(
  request: APIRequestContext,
  token: string,
  overrides?: Partial<{ name: string; description: string; price: number }>,
) {
  const data = {
    name: "Consulta general",
    description: "Consulta veterinaria estándar",
    price: 5000,
    ...overrides,
  };
  const res = await request.post(`${API_BASE}/procedures`, {
    data,
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok()) throw new Error(`createProcedure failed: ${await res.text()}`);
  return (await res.json()) as { id: string; name: string; price: number };
}

export async function fetchClient(
  request: APIRequestContext,
  token: string,
  clientId: string,
) {
  const res = await request.get(`${API_BASE}/clients/${clientId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return { ok: res.ok(), status: res.status(), body: res.ok() ? await res.json() : await res.text() };
}
