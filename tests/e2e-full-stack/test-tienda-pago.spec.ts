import { test, expect } from "@playwright/test";
import {
  setupUser,
  createSupply,
  API_BASE,
} from "./helpers";

test.describe("Flujo tienda: venta + movimiento de caja", () => {
  test("agregar insumo → crear venta → movimiento de caja visible", async ({
    page,
    request,
  }) => {
    // ── Setup ──
    const user = await setupUser(request);
    const supply = await createSupply(request, user.access_token, {
      name: "Collar Antipulgas",
      brand: "Bayer",
      unit_price: 4500,
      stock_quantity: 50,
    });

    // ── Login by setting tokens directly (avoids onboarding race) ──
    await page.goto("/dashboard/tienda");
    await page.evaluate(
      ({ at, rt }: { at: string; rt: string }) => {
        localStorage.setItem("access_token", at);
        localStorage.setItem("refresh_token", rt);
        localStorage.setItem("onboarding_done", "true");
      },
      { at: user.access_token, rt: user.refresh_token },
    );
    await page.reload();
    await expect(page).toHaveURL("/dashboard/tienda");
    await expect(page.getByText("Nueva venta")).toBeVisible();

    // ── Click "Nueva venta" ──
    await page.getByRole("button", { name: "Nueva venta" }).click();
    await expect(page.getByText("Cliente").first()).toBeVisible();

    // ── Step 0: Client name (optional) ──
    await page.getByLabel("Nombre del cliente").fill("Cliente Mostrador");
    await page.getByRole("button", { name: "Continuar" }).click();

    // ── Step 1: Add supply item ──
    await expect(page.getByText("Insumos")).toBeVisible();
    await page.getByLabel("Buscar insumo").fill("Collar");
    await page.locator("text=Collar Antipulgas").first().click();
    await page.getByRole("button", { name: "Agregar" }).click();
    await page.getByRole("button", { name: "Continuar" }).click();

    // ── Step 2: Payment method (Efectivo) ──
    await expect(page.getByText("Pago")).toBeVisible();
    await page.getByRole("button", { name: "Continuar" }).click();

    // ── Step 3: Confirm ──
    await expect(page.getByText("Confirmar venta")).toBeVisible();
    await page.getByRole("button", { name: "Confirmar venta" }).click();

    // ── After creation, verify sale appears in table ──
    await expect(page.getByText("Cliente Mostrador")).toBeVisible();
    await expect(page.getByText("$4.500")).toBeVisible();

    // ── Verify cash movement was created ──
    const movementsRes = await request.get(
      `${API_BASE}/cash/movements?limit=10`,
      { headers: { Authorization: `Bearer ${user.access_token}` } },
    );
    expect(movementsRes.ok()).toBe(true);
    const movements = await movementsRes.json();
    expect(Array.isArray(movements)).toBe(true);
    expect(movements.length).toBeGreaterThanOrEqual(1);

    const saleMovement = movements.find(
      (m: { source_type: string }) => m.source_type === "sale",
    );
    expect(saleMovement).toBeDefined();
    expect(saleMovement.movement_type).toBe("income");
    expect(Number(saleMovement.amount)).toBeGreaterThan(0);
  });
});
