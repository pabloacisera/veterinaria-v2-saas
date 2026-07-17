import { vi } from "vitest";
import {
  fetchMovements,
  fetchMovement,
  createMovement,
  updateMovementStatus,
} from "./api";

vi.mock("@/shared/lib/api", () => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  apiPut: vi.fn(),
  apiDelete: vi.fn(),
  apiPatch: vi.fn(),
}));

import { apiGet, apiPost, apiPatch } from "@/shared/lib/api";

describe("cash api", () => {
  afterEach(() => vi.clearAllMocks());

  it("fetchMovements llama a GET /cash/movements con filtros", async () => {
    vi.mocked(apiGet).mockResolvedValue([]);
    await fetchMovements({ status: "pagado", movement_type: "income" });
    expect(apiGet).toHaveBeenCalledWith("/cash/movements?status=pagado&movement_type=income");
  });

  it("fetchMovement llama a GET /cash/movements/{id}", async () => {
    vi.mocked(apiGet).mockResolvedValue({ id: "m1", amount: 5000 });
    const result = await fetchMovement("m1");
    expect(apiGet).toHaveBeenCalledWith("/cash/movements/m1");
    expect(result).toEqual({ id: "m1", amount: 5000 });
  });

  it("createMovement llama a POST /cash/movements", async () => {
    vi.mocked(apiPost).mockResolvedValue({ id: "m1" });
    await createMovement({ movement_type: "income", amount: 5000, description: "Pago" });
    expect(apiPost).toHaveBeenCalledWith("/cash/movements", {
      movement_type: "income",
      amount: 5000,
      description: "Pago",
    });
  });

  it("updateMovementStatus llama a PATCH /cash/movements/{id}/status", async () => {
    vi.mocked(apiPatch).mockResolvedValue({ id: "m1", status: "pendiente" });
    await updateMovementStatus("m1", "pendiente");
    expect(apiPatch).toHaveBeenCalledWith("/cash/movements/m1/status", { status: "pendiente" });
  });
});
