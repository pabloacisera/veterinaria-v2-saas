import { vi } from "vitest";
import {
  createSale,
  fetchSales,
  fetchSale,
  saveDraft,
  getDraft,
  clearDraft,
} from "./api";

vi.mock("@/shared/lib/api", () => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  apiPut: vi.fn(),
  apiDelete: vi.fn(),
}));

import { apiGet, apiPost, apiDelete } from "@/shared/lib/api";

describe("store api", () => {
  afterEach(() => vi.clearAllMocks());

  it("createSale llama a POST /stores/sales", async () => {
    vi.mocked(apiPost).mockResolvedValue({ id: "sale-1", total: 1210 });
    const result = await createSale({
      items: [{ supply_id: "s1", quantity: 2, unit_price: 500 }],
      payment_method: "efectivo",
    });
    expect(apiPost).toHaveBeenCalledWith("/stores/sales", {
      items: [{ supply_id: "s1", quantity: 2, unit_price: 500 }],
      payment_method: "efectivo",
    });
    expect(result).toEqual({ id: "sale-1", total: 1210 });
  });

  it("fetchSales llama a GET /stores/sales", async () => {
    vi.mocked(apiGet).mockResolvedValue([]);
    await fetchSales({ limit: 20 });
    expect(apiGet).toHaveBeenCalledWith("/stores/sales?limit=20");
  });

  it("fetchSale llama a GET /stores/sales/{id}", async () => {
    vi.mocked(apiGet).mockResolvedValue({ sale: { id: "sale-1" }, items: [] });
    const result = await fetchSale("sale-1");
    expect(apiGet).toHaveBeenCalledWith("/stores/sales/sale-1");
    expect(result).toEqual({ sale: { id: "sale-1" }, items: [] });
  });

  it("saveDraft llama a POST /stores/draft", async () => {
    vi.mocked(apiPost).mockResolvedValue({ status: "ok" });
    await saveDraft(1, { step: 1, data: "test" });
    expect(apiPost).toHaveBeenCalledWith("/stores/draft?step=1", { step: 1, data: "test" });
  });

  it("getDraft llama a GET /stores/draft/current", async () => {
    vi.mocked(apiGet).mockResolvedValue({ step: 1 });
    const result = await getDraft();
    expect(apiGet).toHaveBeenCalledWith("/stores/draft/current");
    expect(result).toEqual({ step: 1 });
  });

  it("clearDraft llama a DELETE /stores/draft/current", async () => {
    vi.mocked(apiDelete).mockResolvedValue(undefined);
    await clearDraft();
    expect(apiDelete).toHaveBeenCalledWith("/stores/draft/current");
  });
});
