import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

// Mock fetch globally
const fetchMock = vi.fn();
vi.stubGlobal("fetch", fetchMock);

// Mock window.location
const locationMock = { href: "" };
Object.defineProperty(window, "location", {
  value: locationMock,
  writable: true,
});

describe("adminApi", () => {
  beforeEach(() => {
    fetchMock.mockReset();
    localStorage.clear();
    locationMock.href = "";
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("adminGet", () => {
    it("sends admin_token in Authorization header", async () => {
      localStorage.setItem("admin_token", "test-admin-jwt");
      fetchMock.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: "test" }),
      });

      const { adminGet } = await import("./adminApi");
      await adminGet("/admin/developer/companias");

      expect(fetchMock).toHaveBeenCalledWith(
        "/api/v1/admin/developer/companias",
        expect.objectContaining({
          method: "GET",
          headers: expect.objectContaining({
            Authorization: "Bearer test-admin-jwt",
          }),
        })
      );
    });

    it("redirects to admin login when no token exists", async () => {
      const { adminGet } = await import("./adminApi");

      await expect(adminGet("/admin/developer/companias")).rejects.toThrow(
        "Sesión de admin expirada"
      );
      expect(locationMock.href).toBe("/access_role/admin/developer");
    });

    it("redirects to admin login on 401 response", async () => {
      localStorage.setItem("admin_token", "expired-token");
      fetchMock.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ detail: "Token expired" }),
      });

      const { adminGet } = await import("./adminApi");

      await expect(adminGet("/admin/developer/companias")).rejects.toThrow(
        "Sesión de admin expirada"
      );
      expect(locationMock.href).toBe("/access_role/admin/developer");
      expect(localStorage.getItem("admin_token")).toBeNull();
    });

    it("throws AdminApiError on non-401 error", async () => {
      localStorage.setItem("admin_token", "test-token");
      fetchMock.mockResolvedValueOnce({
        ok: false,
        status: 403,
        json: () => Promise.resolve({ detail: "Forbidden" }),
      });

      const { adminGet } = await import("./adminApi");

      await expect(adminGet("/admin/developer/companias")).rejects.toThrow(
        "Forbidden"
      );
      // No redirect on 403
      expect(locationMock.href).toBe("");
    });
  });

  describe("adminPost", () => {
    it("sends POST with JSON body and admin_token", async () => {
      localStorage.setItem("admin_token", "test-admin-jwt");
      fetchMock.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ message: "ok" }),
      });

      const { adminPost } = await import("./adminApi");
      await adminPost("/admin/developer/companias/123/bloquear", {});

      expect(fetchMock).toHaveBeenCalledWith(
        "/api/v1/admin/developer/companias/123/bloquear",
        expect.objectContaining({
          method: "POST",
          headers: expect.objectContaining({
            Authorization: "Bearer test-admin-jwt",
            "Content-Type": "application/json",
          }),
          body: "{}",
        })
      );
    });
  });

  describe("adminGetBlob", () => {
    it("returns blob on success with admin_token", async () => {
      localStorage.setItem("admin_token", "test-admin-jwt");
      const mockBlob = new Blob(["csv-data"], { type: "text/csv" });
      fetchMock.mockResolvedValueOnce({
        ok: true,
        status: 200,
        blob: () => Promise.resolve(mockBlob),
      });

      const { adminGetBlob } = await import("./adminApi");
      const result = await adminGetBlob("/admin/developer/exportar/companias");

      expect(result).toEqual(mockBlob);
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/v1/admin/developer/exportar/companias",
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: "Bearer test-admin-jwt",
          }),
        })
      );
    });

    it("redirects to admin login on 401", async () => {
      localStorage.setItem("admin_token", "expired-token");
      fetchMock.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ detail: "Unauthorized" }),
      });

      const { adminGetBlob } = await import("./adminApi");

      await expect(
        adminGetBlob("/admin/developer/exportar/companias")
      ).rejects.toThrow("Sesión de admin expirada");
      expect(locationMock.href).toBe("/access_role/admin/developer");
    });
  });
});
