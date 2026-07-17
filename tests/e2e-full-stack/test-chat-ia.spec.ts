import { test, expect } from "@playwright/test";
import { setupUser, TEST_PASSWORD, randomEmail } from "./helpers";

test.describe("Chat IA", () => {
  test("acceder al chat → ver UI → enviar mensaje → recibir respuesta (o error controlado)", async ({
    page,
    request,
  }) => {
    // ── Setup authenticated user ──
    const { email } = await setupUser(request);

    // ── Login via UI ──
    await page.goto("/login");
    await page.getByLabel("Email").fill(email);
    await page.getByLabel("Contraseña").fill(TEST_PASSWORD);
    await page.getByRole("button", { name: "Iniciar sesión" }).click();
    await page.evaluate(() => localStorage.setItem("onboarding_done", "true"));
    await page.goto("/dashboard");

    // ── Navigate to Chat ──
    await page.getByRole("button", { name: "IA Chat" }).click();
    await expect(page).toHaveURL("/dashboard/chat");

    // ── Verify chat UI renders ──
    await expect(page.getByText("Asistente IA")).toBeVisible();
    await expect(page.getByText("Historial")).toBeVisible();
    await expect(
      page.getByPlaceholder("Escribí tu mensaje..."),
    ).toBeVisible();

    // ── Send a message ──
    const input = page.getByPlaceholder("Escribí tu mensaje...");
    await input.fill("¿Cuántos clientes tengo?");
    await input.press("Enter");

    // ── Wait for response ──
    // The LLM may not be available in CI, so we accept either:
    //   a) A streaming response (message content appears)
    //   b) An error message about quota / API key / timeout
    //   c) The input becomes enabled again (request finished)
    await page.waitForFunction(
      () => {
        const input = document.querySelector<HTMLInputElement>(
          'input[placeholder="Escribí tu mensaje..."], textarea[placeholder="Escribí tu mensaje..."]',
        );
        return input && !input.disabled;
      },
      { timeout: 30_000 },
    );

    // ── Verify user message is displayed ──
    await expect(page.getByText("¿Cuántos clientes tengo?")).toBeVisible();
  });
});
