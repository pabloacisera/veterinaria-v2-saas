import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

const fetchMock = vi.fn();
vi.stubGlobal("fetch", fetchMock);

const locationMock = { href: "" };
Object.defineProperty(window, "location", {
  value: locationMock,
  writable: true,
});

describe("clientApi", () => {
  beforeEach(() => {
    fetchMock.mockReset();
    localStorage.clear();
    locationMock.href = "";
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("clientGet", () => {
    it("sends client_token in Authorization header", async () => {
      localStorage.setItem("client_token", "test-client-jwt");
      fetchMock.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve([{ id: "1", nombre: "Firulais" }]),
      });

      const { clientGet } = await import("./clientApi");
      const result = await clientGet("/cliente/mis-mascotas");

      expect(fetchMock).toHaveBeenCalledWith(
        "/api/v1/cliente/mis-mascotas",
        expect.objectContaining({
          method: "GET",
          headers: expect.objectContaining({
            Authorization: "Bearer test-client-jwt",
          }),
        })
      );
      expect(result).toEqual([{ id: "1", nombre: "Firulais" }]);
    });

    it("redirects to /cliente/acceso when no token exists", async () => {
      const { clientGet } = await import("./clientApi");

      await expect(clientGet("/cliente/mis-mascotas")).rejects.toThrow(
        "Sesión de cliente expirada"
      );
      expect(locationMock.href).toBe("/cliente/acceso");
    });

    it("redirects to /cliente/acceso on 401 response", async () => {
      localStorage.setItem("client_token", "expired-token");
      fetchMock.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ detail: "Token expired" }),
      });

      const { clientGet } = await import("./clientApi");

      await expect(clientGet("/cliente/mis-mascotas")).rejects.toThrow(
        "Sesión de cliente expirada"
      );
      expect(locationMock.href).toBe("/cliente/acceso");
      expect(localStorage.getItem("client_token")).toBeNull();
    });

    it("throws ClientApiError on non-401 error", async () => {
      localStorage.setItem("client_token", "test-token");
      fetchMock.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: "Internal error" }),
      });

      const { clientGet } = await import("./clientApi");

      await expect(clientGet("/cliente/mis-mascotas")).rejects.toThrow(
        "Internal error"
      );
      expect(locationMock.href).toBe("");
    });
  });

  describe("clientPost", () => {
    it("sends POST with JSON body and client_token", async () => {
      localStorage.setItem("client_token", "test-client-jwt");
      fetchMock.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ ok: true }),
      });

      const { clientPost } = await import("./clientApi");
      await clientPost("/cliente/alguna-accion", { dato: "valor" });

      expect(fetchMock).toHaveBeenCalledWith(
        "/api/v1/cliente/alguna-accion",
        expect.objectContaining({
          method: "POST",
          headers: expect.objectContaining({
            Authorization: "Bearer test-client-jwt",
            "Content-Type": "application/json",
          }),
          body: JSON.stringify({ dato: "valor" }),
        })
      );
    });
  });
});
