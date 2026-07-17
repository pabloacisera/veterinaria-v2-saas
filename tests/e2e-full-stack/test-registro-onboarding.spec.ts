import { test, expect } from "@playwright/test";
import {
  randomEmail,
  TEST_PASSWORD,
  getActivationCode,
} from "./helpers";

test.describe("Registro y onboarding", () => {
  test("flujo completo: registro → activación → login → onboarding → dashboard", async ({
    page,
  }) => {
    const email = randomEmail();

    // 1. Landing → Register
    await page.goto("/");
    await page.getByRole("button", { name: "Registrarse" }).first().click();
    await expect(page).toHaveURL("/register");
    await expect(page.getByText("Crear cuenta")).toBeVisible();

    // 2. Fill register form
    await page.getByLabel("Nombre").fill("Juan");
    await page.getByLabel("Apellido").fill("Pérez");
    await page.getByLabel("Email").fill(email);
    await page.getByLabel("Contraseña").fill(TEST_PASSWORD);
    await page.getByLabel("Nombre de la empresa").fill("Veterinaria E2E");
    await page.getByLabel("CUIT").fill("20-12345678-9");
    await page.getByRole("button", { name: "Crear cuenta" }).click();

    // 3. Wait for activation form
    await expect(page.getByText("Activá tu cuenta")).toBeVisible();
    await expect(page.getByText(email)).toBeVisible();

    // 4. Retrieve activation code from Redis
    const code = await getActivationCode(email);
    expect(code).toMatch(/^\d{6}$/);

    // 5. Enter activation code
    await page.getByLabel("Código de activación").fill(code);
    await page.getByRole("button", { name: "Activar cuenta" }).click();

    // 6. Verify redirect to login with success banner
    await expect(page).toHaveURL(/\/login\?activated=true/);
    await expect(page.getByText("Cuenta activada correctamente")).toBeVisible();

    // 7. Login
    await page.getByLabel("Email").fill(email);
    await page.getByLabel("Contraseña").fill(TEST_PASSWORD);
    await page.getByRole("button", { name: "Iniciar sesión" }).click();

    // 8. Onboarding wizard appears
    await expect(page.getByText("¡Bienvenido a Veter!")).toBeVisible();

    // 9. Step 0 → click Comenzar
    await page.getByRole("button", { name: "Comenzar" }).click();

    // 10. Step 1: First client
    await expect(page.getByText("Registrá tu primer cliente")).toBeVisible();
    await page.getByLabel("Nombre").fill("Ana");
    await page.getByLabel("Apellido").fill("Martínez");
    await page.getByLabel("Email").fill("ana@ejemplo.com");
    await page.getByLabel("Tipo Doc.").fill("DNI");
    await page.getByLabel("Número").fill("30123456");
    await page.getByLabel("Teléfono").fill("1155556666");
    await page.getByRole("button", { name: "Guardar cliente" }).click();

    // 11. Step 2: First pet
    await expect(page.getByText("Registrá la primera mascota")).toBeVisible();
    await page.getByLabel("Nombre").fill("Max");
    await page.getByLabel("Especie").fill("Perro");
    await page.getByLabel("Raza").fill("Golden");
    await page.getByLabel("Sexo").fill("Macho");
    await page.getByLabel("Color").fill("Dorado");
    await page.getByLabel("Fecha nac.").fill("2024-01-15");
    await page.getByRole("button", { name: "Guardar mascota" }).click();

    // 12. Step 3: Done
    await expect(page.getByText("¡Todo listo!")).toBeVisible();
    await page.getByRole("button", { name: "Ir al Dashboard" }).click();

    // 13. Verify dashboard home
    await expect(page.getByText("Dashboard")).toBeVisible();
    await expect(page.getByText("Resumen de tu veterinaria")).toBeVisible();
    await expect(page.getByText("Clientes")).toBeVisible();
    await expect(page.getByText("Mascotas")).toBeVisible();
  });
});
