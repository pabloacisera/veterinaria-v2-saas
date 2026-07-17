import { test, expect } from "@playwright/test";
import {
  setupUser,
  createClient,
  createPet,
  createSupply,
  createProcedure,
  API_BASE,
} from "./helpers";

test.describe("Flujo clínico: consulta + factura", () => {
  test("crear cliente → mascota → consulta con procedimientos → descargar factura", async ({
    page,
    request,
  }) => {
    // ── Setup: register + seed data via API ──
    const user = await setupUser(request);
    const client = await createClient(request, user.access_token);
    const pet = await createPet(request, user.access_token, client.id);
    const supply = await createSupply(request, user.access_token, {
      name: "Vacuna Antirrábica",
      unit_price: 3500,
    });
    const procedure = await createProcedure(request, user.access_token, {
      name: "Consulta clínica",
      price: 5000,
    });

    // ── Login by setting tokens directly ──
    await page.goto("/dashboard/consultas");
    await page.evaluate(
      ({ at, rt }: { at: string; rt: string }) => {
        localStorage.setItem("access_token", at);
        localStorage.setItem("refresh_token", rt);
        localStorage.setItem("onboarding_done", "true");
      },
      { at: user.access_token, rt: user.refresh_token },
    );
    await page.reload();
    await expect(page).toHaveURL("/dashboard/consultas");
    await expect(page.getByText("Nueva consulta")).toBeVisible();

    // ── Click "Nueva consulta" ──
    await page.getByRole("button", { name: "Nueva consulta" }).click();
    await expect(page.getByText("Seleccionar paciente")).toBeVisible();

    // ── Step 0: Select client & pet ──
    await page.getByLabel("Buscar cliente").fill(client.name);
    await page.locator("text=María García").first().click();
    await page.getByLabel("Buscar mascota").fill("Firulais");
    await page.locator("text=Firulais").first().click();
    await page.getByRole("button", { name: "Continuar" }).click();

    // ── Step 1: Reason & diagnosis ──
    await expect(page.getByText("Datos de la consulta")).toBeVisible();
    await page.getByLabel("Motivo de consulta").fill("Revisión general");
    await page.getByLabel("Diagnóstico").fill("Paciente sano");
    await page.getByRole("button", { name: "Continuar" }).click();

    // ── Step 2: Add procedure ──
    await expect(page.getByText("Procedimientos")).toBeVisible();
    await page.getByLabel("Agregar procedimiento").fill("Consulta");
    await page.locator("text=Consulta clínica").first().click();
    await page.getByRole("button", { name: "Continuar" }).click();

    // ── Step 3: Add supply ──
    await expect(page.getByText("Insumos")).toBeVisible();
    await page.getByLabel("Agregar insumo").fill("Vacuna");
    await page.locator("text=Vacuna Antirrábica").first().click();
    await page.getByRole("button", { name: "Continuar" }).click();

    // ── Step 4: Payment method (default Efectivo) ──
    await expect(page.getByText("Método de pago")).toBeVisible();
    await page.getByRole("button", { name: "Continuar" }).click();

    // ── Step 5: Confirm ──
    await expect(page.getByText("Confirmar consulta")).toBeVisible();
    await page.getByRole("button", { name: "Confirmar consulta" }).click();

    // ── After creation, verify consultation appears in table ──
    await expect(page.getByText("Revisión general")).toBeVisible();
    await expect(page.getByText("Paciente sano")).toBeVisible();

    // ── Click Factura button ──
    const [downloadResponse] = await Promise.all([
      page.waitForResponse((res) =>
        res.url().includes("/consultations/") && res.url().includes("/factura") && res.status() === 200,
      ),
      page.getByRole("button", { name: "Factura" }).first().click(),
    ]);

    const facturaBody = await downloadResponse.json();
    expect(facturaBody).toHaveProperty("download_url");
    expect(facturaBody.download_url).toBeTruthy();

    // ── Also verify the consultation details via API ──
    const detailRes = await request.get(
      `${API_BASE}/consultations/${facturaBody.public_id}`,
      { headers: { Authorization: `Bearer ${user.access_token}` } },
    );
    expect(detailRes.ok()).toBe(true);
  });
});
