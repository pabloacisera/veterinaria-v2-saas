import { test, expect } from "@playwright/test";
import {
  setupUser,
  createClient,
  API_BASE,
} from "./helpers";

test.describe("Aislamiento entre tenants", () => {
  test("Tenant B no puede acceder a datos de Tenant A", async ({
    page,
    request,
  }) => {
    // ── Tenant A: register + create client ──
    const tenantA = await setupUser(request);
    const clientA = await createClient(request, tenantA.access_token, {
      name: "ClienteA",
      surname: "DeTenantA",
      email: `tenanta_${Date.now()}@test.com`,
    });

    // ── Tenant B: register (completely separate) ──
    const tenantB = await setupUser(request);

    // ── Tenant B tries to fetch Tenant A's client via API ──
    const fetchRes = await request.get(
      `${API_BASE}/clients/${clientA.id}`,
      { headers: { Authorization: `Bearer ${tenantB.access_token}` } },
    );
    // Expect 404 – the client belongs to a different company
    expect(fetchRes.status()).toBe(404);

    // ── Tenant B tries to list clients – should see empty ──
    const listRes = await request.get(`${API_BASE}/clients?limit=10`, {
      headers: { Authorization: `Bearer ${tenantB.access_token}` },
    });
    expect(listRes.ok()).toBe(true);
    const clientsB = await listRes.json();
    expect(Array.isArray(clientsB)).toBe(true);
    expect(clientsB.length).toBe(0);

    // ── Login as Tenant B via stored tokens + navigate to clients ──
    await page.goto("/dashboard/clientes");
    await page.evaluate(
      ({ at, rt }: { at: string; rt: string }) => {
        localStorage.setItem("access_token", at);
        localStorage.setItem("refresh_token", rt);
        localStorage.setItem("onboarding_done", "true");
      },
      { at: tenantB.access_token, rt: tenantB.refresh_token },
    );
    await page.goto("/dashboard/clientes");

    await expect(page.getByText("Clientes")).toBeVisible();
    await expect(page.getByText(/No hay clientes|Sin resultados/i)).toBeVisible();
  });
});
